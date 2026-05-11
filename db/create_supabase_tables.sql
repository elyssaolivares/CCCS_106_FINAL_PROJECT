-- SQL to create audit and activity tables for Supabase (public schema)
create table if not exists public.audit_logs (
    id bigserial primary key,
    actor_email text not null,
    actor_name text,
    action_type text not null,
    resource_type text,
    resource_id bigint,
    details text,
    timestamp timestamptz default now(),
    status text default 'success'
);

create table if not exists public.user_activity (
    id bigserial primary key,
    user_email text not null,
    user_name text,
    activity_type text not null,
    ip_address text,
    location_country text,
    location_city text,
    location_isp text,
    device_info text,
    status text default 'success',
    details text,
    timestamp timestamptz default now()
);

create table if not exists public.user_login_stats (
    id bigserial primary key,
    user_email text unique not null,
    last_login timestamptz,
    last_login_ip text,
    last_login_location text,
    total_logins integer default 0,
    total_failed_attempts integer default 0,
    last_failed_attempt timestamptz,
    account_locked integer default 0,
    lock_until timestamptz
);

create table if not exists public.failed_login_attempts (
    id bigserial primary key,
    email text not null,
    ip_address text,
    location text,
    reason text,
    timestamp timestamptz default now()
);

create index if not exists idx_audit_logs_actor_email on public.audit_logs(actor_email);
create index if not exists idx_audit_logs_action_type on public.audit_logs(action_type);
create index if not exists idx_audit_logs_timestamp on public.audit_logs(timestamp);

create index if not exists idx_user_activity_email on public.user_activity(user_email);
create index if not exists idx_user_activity_type on public.user_activity(activity_type);
create index if not exists idx_user_activity_timestamp on public.user_activity(timestamp);

create index if not exists idx_login_stats_email on public.user_login_stats(user_email);
create index if not exists idx_failed_attempts_email on public.failed_login_attempts(email);
create index if not exists idx_failed_attempts_timestamp on public.failed_login_attempts(timestamp);
