create extension if not exists "uuid-ossp";

create table if not exists projects (
  id uuid primary key default uuid_generate_v4(),
  user_id uuid,
  brand_name text,
  language text default 'English',
  aspect_ratio text default '9:16',
  status text default 'processing',
  product_analysis jsonb,
  ad_plan jsonb,
  video_job_id text,
  video_url text,
  template_url text,
  stickers jsonb default '[]'::jsonb,
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

create index if not exists projects_user_id_idx on projects(user_id);
create index if not exists projects_created_at_idx on projects(created_at desc);
