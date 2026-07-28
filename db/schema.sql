-- estimand DB: uncertainty numbers that cannot be compared illegally.
--
-- The Python layer refuses incommensurable contrasts. That refusal is worthless
-- if a future agent writes the row by hand. So the same rule is enforced here,
-- in a trigger, where prose cannot reach it.
--
-- HB8: every axis takes the strictest feasible type. pairing, distance, unit and
-- verdict are ENUMs, not text, because free text is how "ref|draw" and
-- "ref_draw" and "reference vs draw" become three values of one concept and the
-- GROUP BY that would have caught the bug silently splits.

BEGIN;

DROP SCHEMA IF EXISTS est CASCADE;
CREATE SCHEMA est;
SET search_path TO est, public;

CREATE TYPE pairing_t AS ENUM (
  'ref|ref',                  -- neither endpoint resampled
  'ref|draw',                 -- one reference, one draw
  'draw|draw(coupled)',       -- both draws, SAME draw
  'draw|draw(independent)'    -- both draws, independent
);

CREATE TYPE distance_t AS ENUM ('signed_jaccard', 'jaccard', 'l2', 'tv', 'kendall_tau');
CREATE TYPE unit_t     AS ENUM ('participants', 'prompts', 'items', 'sessions', 'annotations');
CREATE TYPE verdict_t  AS ENUM ('left_dominates', 'right_dominates', 'indistinguishable', 'undefined');
CREATE TYPE source_t   AS ENUM ('synthetic_oracle', 'coval_release', 'external_reanalysis');

-- ---------------------------------------------------------------- runs
CREATE TABLE run (
  id          bigserial PRIMARY KEY,
  started_at  timestamptz NOT NULL DEFAULT now(),
  source      source_t    NOT NULL,
  code_sha    text        NOT NULL,
  seed        bigint      NOT NULL,
  draws       integer     NOT NULL CHECK (draws > 0),
  note        text        NOT NULL DEFAULT ''
);

-- ---------------------------------------------------------------- estimands
CREATE TABLE estimand (
  id            bigserial PRIMARY KEY,
  run_id        bigint      NOT NULL REFERENCES run(id) ON DELETE CASCADE,
  statistic     text        NOT NULL,
  perturbation  text        NOT NULL,
  pairing       pairing_t   NOT NULL,
  distance      distance_t  NOT NULL,
  unit          unit_t      NOT NULL,
  population    text        NOT NULL,
  value         double precision NOT NULL,
  n_pairs       integer     NOT NULL CHECK (n_pairs >= 0),
  support_lo    double precision NOT NULL DEFAULT 0.0,
  support_hi    double precision NOT NULL DEFAULT 1.0,
  ci_lo         double precision,
  ci_hi         double precision,
  note          text        NOT NULL DEFAULT '',
  CONSTRAINT value_in_support CHECK (value >= support_lo AND value <= support_hi),
  CONSTRAINT ci_ordered       CHECK (ci_lo IS NULL OR ci_hi IS NULL OR ci_lo <= ci_hi),
  CONSTRAINT one_row_per_cell UNIQUE (run_id, statistic, perturbation, pairing, distance, unit, population)
);

CREATE INDEX estimand_cell_idx ON estimand (statistic, perturbation, pairing);

-- ---------------------------------------------------------------- contrasts
CREATE TABLE contrast (
  id        bigserial PRIMARY KEY,
  run_id    bigint  NOT NULL REFERENCES run(id) ON DELETE CASCADE,
  left_id   bigint  NOT NULL REFERENCES estimand(id) ON DELETE CASCADE,
  right_id  bigint  NOT NULL REFERENCES estimand(id) ON DELETE CASCADE,
  value     double precision NOT NULL,
  ci_lo     double precision,
  ci_hi     double precision,
  verdict   verdict_t NOT NULL,
  CONSTRAINT not_self CHECK (left_id <> right_id)
);

-- The enforcement point. A contrast whose sides differ in statistic, distance,
-- pairing or unit is not a weaker result -- it is not a result. Refuse the write.
CREATE OR REPLACE FUNCTION est.assert_commensurable() RETURNS trigger AS $$
DECLARE l est.estimand%ROWTYPE; r est.estimand%ROWTYPE; why text := '';
BEGIN
  SELECT * INTO l FROM est.estimand WHERE id = NEW.left_id;
  SELECT * INTO r FROM est.estimand WHERE id = NEW.right_id;

  IF l.statistic IS DISTINCT FROM r.statistic THEN
    why := why || format('statistic %L vs %L; ', l.statistic, r.statistic);
  END IF;
  IF l.distance IS DISTINCT FROM r.distance THEN
    why := why || format('distance %L vs %L; ', l.distance, r.distance);
  END IF;
  IF l.pairing IS DISTINCT FROM r.pairing THEN
    why := why || format(
      'pairing %L vs %L -- a distance-to-centre and a distance-between-draws '
      'differ by construction, so their difference has a sign fixed before any '
      'data is seen; ', l.pairing, r.pairing);
  END IF;
  IF l.unit IS DISTINCT FROM r.unit OR l.population IS DISTINCT FROM r.population THEN
    why := why || format('frame (%L,%L) vs (%L,%L); ',
                         l.unit, l.population, r.unit, r.population);
  END IF;
  IF l.perturbation IS NOT DISTINCT FROM r.perturbation THEN
    why := why || format('both sides perturb %L; ', l.perturbation);
  END IF;

  IF why <> '' THEN
    RAISE EXCEPTION 'incommensurable contrast refused: %', why
      USING HINT = 'measure both sides under the same pairing, or report the lattice';
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contrast_commensurable
  BEFORE INSERT OR UPDATE ON contrast
  FOR EACH ROW EXECUTE FUNCTION est.assert_commensurable();

-- ---------------------------------------------------------------- oracle cells
CREATE TABLE oracle_cell (
  id             bigserial PRIMARY KEY,
  run_id         bigint NOT NULL REFERENCES run(id) ON DELETE CASCADE,
  n              integer NOT NULL CHECK (n > 0),
  k              integer NOT NULL CHECK (k > 0),
  polarization   double precision NOT NULL CHECK (polarization BETWEEN 0 AND 1),
  signal_gap     double precision NOT NULL CHECK (signal_gap > 0),
  style_sd       double precision NOT NULL CHECK (style_sd >= 0),
  n_items        integer NOT NULL CHECK (n_items > 0),
  seed           integer NOT NULL,
  rule_set       text    NOT NULL,
  oracle_sample  double precision NOT NULL,
  oracle_rule    double precision NOT NULL,
  oracle_gdi     double precision NOT NULL,
  truth_sign     smallint NOT NULL CHECK (truth_sign IN (-1, 1)),
  truth_margin   double precision NOT NULL CHECK (truth_margin >= 0),
  CONSTRAINT gdi_consistent CHECK (abs(oracle_gdi - (oracle_rule - oracle_sample)) < 1e-9)
);

CREATE TABLE estimator_result (
  cell_id        bigint NOT NULL REFERENCES oracle_cell(id) ON DELETE CASCADE,
  estimator      text   NOT NULL,
  mean_value     double precision NOT NULL,
  bias           double precision NOT NULL,
  sign_recovery  double precision NOT NULL CHECK (sign_recovery BETWEEN 0 AND 1),
  PRIMARY KEY (cell_id, estimator)
);

-- ---------------------------------------------------------------- views
CREATE VIEW pairing_lattice AS
SELECT statistic, perturbation, pairing, distance, unit,
       avg(value) AS value, sum(n_pairs) AS n_pairs, count(*) AS rows
FROM estimand GROUP BY 1,2,3,4,5 ORDER BY 1,2,3;

-- Where does the verdict depend on the pairing rather than on the data?
CREATE VIEW sign_flip_by_pairing AS
SELECT c.left_id, l.statistic, l.perturbation AS left_pert, r.perturbation AS right_pert,
       l.pairing, c.value, c.verdict
FROM contrast c
JOIN estimand l ON l.id = c.left_id
JOIN estimand r ON r.id = c.right_id
ORDER BY l.statistic, l.perturbation, l.pairing;

CREATE VIEW estimator_scoreboard AS
SELECT e.estimator,
       count(*)                       AS cells,
       avg(e.sign_recovery)           AS mean_sign_recovery,
       avg(abs(e.bias))               AS mean_abs_bias,
       sum((e.sign_recovery < 0.5)::int) AS cells_worse_than_coin
FROM estimator_result e GROUP BY 1 ORDER BY 3 DESC;

COMMIT;
