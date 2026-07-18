-- CardWise production-oriented PostgreSQL schema
-- Money uses integer paise/minor units. Product facts are effective-dated.

create extension if not exists pgcrypto;
create extension if not exists btree_gist;

create table issuers (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  legal_name text,
  website_url text not null,
  active boolean not null default true,
  created_at timestamptz not null default now()
);

create type card_status as enum ('draft','active','paused','discontinued');
create type review_status as enum ('pending','verified','rejected','stale');
create type source_type as enum ('product_page','mitc','terms_pdf','reward_catalogue','partner_feed','editorial');

create table cards (
  id uuid primary key default gen_random_uuid(),
  issuer_id uuid not null references issuers(id),
  canonical_name text not null,
  network text,
  variant text,
  secured boolean not null default false,
  cobranded boolean not null default false,
  status card_status not null default 'draft',
  application_url text,
  unique (issuer_id, canonical_name, variant)
);

create table sources (
  id uuid primary key default gen_random_uuid(),
  url text not null,
  source_type source_type not null,
  issuer_owned boolean not null default false,
  fetched_at timestamptz,
  content_hash text,
  archive_object_key text,
  http_status integer,
  unique (url, content_hash)
);

create table source_snapshots (
  id uuid primary key default gen_random_uuid(),
  source_id uuid not null references sources(id) on delete cascade,
  observed_at timestamptz not null default now(),
  http_status integer,
  content_hash text not null,
  archive_object_key text not null,
  parser_name text,
  parser_version text,
  unique (source_id, content_hash)
);

create table card_versions (
  id uuid primary key default gen_random_uuid(),
  card_id uuid not null references cards(id),
  version_no integer not null,
  effective_from date not null,
  effective_to date,
  observed_from timestamptz not null default now(),
  observed_to timestamptz,
  joining_fee_minor bigint not null default 0 check (joining_fee_minor >= 0),
  annual_fee_minor bigint not null default 0 check (annual_fee_minor >= 0),
  fee_tax_rate numeric(7,6) not null default 0,
  waiver_spend_minor bigint check (waiver_spend_minor >= 0),
  forex_markup_rate numeric(7,6),
  min_income_minor bigint,
  source_id uuid references sources(id),
  verified_at timestamptz,
  verified_by text,
  review_status review_status not null default 'pending',
  notes text,
  unique (card_id, version_no),
  exclude using gist (card_id with =, daterange(effective_from, coalesce(effective_to, 'infinity'::date), '[]') with &&)
);

create table extracted_facts (
  id uuid primary key default gen_random_uuid(),
  source_snapshot_id uuid not null references source_snapshots(id) on delete cascade,
  card_id uuid references cards(id),
  fact_type text not null,
  fact_payload jsonb not null,
  citation_locator text,
  confidence numeric(4,3) check (confidence between 0 and 1),
  review_status review_status not null default 'pending',
  reviewed_by text,
  reviewed_at timestamptz
);

create table categories (
  id smallserial primary key,
  slug text not null unique,
  label text not null
);

create table reward_programs (
  id uuid primary key default gen_random_uuid(),
  card_version_id uuid not null references card_versions(id) on delete cascade,
  currency_name text not null,
  default_point_value_minor numeric(12,4),
  expiry_months integer,
  valuation_notes text
);

create table reward_rules (
  id uuid primary key default gen_random_uuid(),
  reward_program_id uuid not null references reward_programs(id) on delete cascade,
  category_id smallint references categories(id),
  merchant_filter jsonb not null default '{}'::jsonb,
  earn_numerator numeric(14,6) not null,
  earn_denominator_minor bigint not null check (earn_denominator_minor > 0),
  point_value_minor numeric(12,4),
  cap_minor bigint,
  cap_period text check (cap_period in ('transaction','monthly','quarterly','annual','none')),
  min_txn_minor bigint,
  rounding_rule text,
  exclusion_expression jsonb not null default '{}'::jsonb,
  rule_priority integer not null default 100,
  effective_from date not null,
  effective_to date,
  source_id uuid references sources(id)
);

create table benefits (
  id uuid primary key default gen_random_uuid(),
  card_version_id uuid not null references card_versions(id) on delete cascade,
  benefit_type text not null,
  quantity numeric(12,2),
  period text,
  estimated_value_minor bigint,
  condition_expression jsonb not null default '{}'::jsonb,
  notes text,
  source_id uuid references sources(id)
);

create table eligibility_rules (
  id uuid primary key default gen_random_uuid(),
  card_version_id uuid not null references card_versions(id) on delete cascade,
  employment_type text,
  min_income_minor bigint,
  min_age smallint,
  max_age smallint,
  geography_expression jsonb not null default '{}'::jsonb,
  credit_profile_hint text,
  secured_deposit_min_minor bigint,
  evidence_strength text not null default 'unknown' check (evidence_strength in ('issuer','partner','editorial','unknown')),
  notes text,
  source_id uuid references sources(id)
);

create table partners (
  id uuid primary key default gen_random_uuid(),
  name text not null unique,
  relationship_disclosure text not null
);

create table affiliate_offers (
  id uuid primary key default gen_random_uuid(),
  card_id uuid not null references cards(id),
  partner_id uuid not null references partners(id),
  destination_url text not null,
  payout_model text,
  starts_at timestamptz,
  ends_at timestamptz,
  disclosure_text text not null,
  active boolean not null default true
);

create table rulesets (
  id uuid primary key default gen_random_uuid(),
  semantic_version text not null unique,
  config jsonb not null,
  published_at timestamptz,
  notes text
);

create table recommendation_runs (
  id uuid primary key default gen_random_uuid(),
  anonymous_profile_id uuid,
  ruleset_id uuid not null references rulesets(id),
  catalogue_snapshot_at timestamptz not null,
  input_json jsonb not null,
  consent_context jsonb,
  created_at timestamptz not null default now()
);

create table consent_records (
  id uuid primary key default gen_random_uuid(),
  anonymous_profile_id uuid,
  purpose text not null,
  notice_version text not null,
  notice_text_hash text not null,
  granted boolean not null,
  channel text not null,
  recorded_at timestamptz not null default now(),
  withdrawn_at timestamptz
);

create table recommendation_results (
  run_id uuid not null references recommendation_runs(id) on delete cascade,
  card_version_id uuid not null references card_versions(id),
  rank integer not null check (rank > 0),
  fit_score numeric(6,3) not null check (fit_score between 0 and 100),
  eligibility_confidence text not null check (eligibility_confidence in ('strong','possible','weak','unknown')),
  gross_value_minor bigint not null,
  annual_fee_minor bigint not null,
  net_value_minor bigint not null,
  explanation_json jsonb not null,
  primary key (run_id, card_version_id),
  unique (run_id, rank)
);

create table calculation_traces (
  id uuid primary key default gen_random_uuid(),
  run_id uuid not null references recommendation_runs(id) on delete cascade,
  card_version_id uuid not null references card_versions(id),
  month smallint check (month between 1 and 12),
  category_id smallint references categories(id),
  eligible_spend_minor bigint not null,
  reward_rule_id uuid references reward_rules(id),
  reward_value_minor bigint not null,
  cap_applied boolean not null default false,
  explanation jsonb not null default '{}'::jsonb
);

create index card_versions_current_idx on card_versions(card_id, effective_from desc) where effective_to is null;
create index reward_rules_program_idx on reward_rules(reward_program_id, rule_priority, effective_from);
create index recommendation_runs_created_idx on recommendation_runs(created_at desc);
create index source_snapshots_observed_idx on source_snapshots(source_id, observed_at desc);
create index calculation_traces_run_idx on calculation_traces(run_id, card_version_id, month);

comment on table affiliate_offers is 'Commercial availability is deliberately separate from organic recommendation scoring.';
comment on table recommendation_runs is 'Input should avoid direct identifiers unless a separate, consented account feature requires them.';
