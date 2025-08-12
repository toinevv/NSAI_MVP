-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.analysis_results (
  session_id uuid NOT NULL,
  processing_started_at timestamp with time zone,
  processing_completed_at timestamp with time zone,
  processing_time_seconds integer,
  raw_gpt_response jsonb,
  error_message text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  status character varying DEFAULT 'queued'::character varying CHECK (status::text = ANY (ARRAY['queued'::character varying, 'processing'::character varying, 'completed'::character varying, 'failed'::character varying]::text[])),
  gpt_version character varying DEFAULT 'gpt-4-vision-preview'::character varying,
  frames_analyzed integer DEFAULT 0,
  analysis_cost numeric DEFAULT 0.00,
  confidence_score numeric DEFAULT 0.00 CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00),
  structured_insights jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT analysis_results_pkey PRIMARY KEY (id),
  CONSTRAINT analysis_results_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);
CREATE TABLE public.automation_opportunities (
  analysis_id uuid NOT NULL,
  session_id uuid NOT NULL,
  opportunity_type character varying NOT NULL,
  title character varying NOT NULL,
  description text NOT NULL,
  current_time_per_occurrence_seconds integer,
  implementation_effort_hours integer,
  estimated_cost_savings_monthly numeric,
  estimated_implementation_cost numeric,
  roi_percentage numeric,
  payback_period_days integer,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  workflow_steps ARRAY DEFAULT '{}'::text[],
  occurrences_per_day integer DEFAULT 1,
  automation_complexity character varying DEFAULT 'medium'::character varying CHECK (automation_complexity::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying]::text[])),
  confidence_score numeric DEFAULT 0.00 CHECK (confidence_score >= 0.00 AND confidence_score <= 1.00),
  priority character varying DEFAULT 'medium'::character varying CHECK (priority::text = ANY (ARRAY['low'::character varying, 'medium'::character varying, 'high'::character varying, 'critical'::character varying]::text[])),
  CONSTRAINT automation_opportunities_pkey PRIMARY KEY (id),
  CONSTRAINT automation_opportunities_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis_results(id),
  CONSTRAINT automation_opportunities_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);
CREATE TABLE public.cost_analyses (
  analysis_id uuid NOT NULL,
  session_id uuid NOT NULL,
  current_monthly_hours numeric,
  current_monthly_cost numeric,
  projected_monthly_hours numeric,
  projected_monthly_cost numeric,
  total_implementation_cost numeric,
  monthly_savings numeric,
  annual_savings numeric,
  payback_period_days integer,
  roi_percentage numeric,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  current_hourly_rate numeric DEFAULT 25.00,
  confidence_level character varying DEFAULT 'medium'::character varying,
  assumptions jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT cost_analyses_pkey PRIMARY KEY (id),
  CONSTRAINT cost_analyses_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis_results(id),
  CONSTRAINT cost_analyses_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);
CREATE TABLE public.generated_reports (
  analysis_id uuid NOT NULL,
  session_id uuid NOT NULL,
  report_type character varying NOT NULL CHECK (report_type::text = ANY (ARRAY['pdf'::character varying, 'excel'::character varying, 'shareable_link'::character varying, 'json_export'::character varying]::text[])),
  file_url text,
  file_size_bytes bigint,
  access_token character varying,
  expires_at timestamp with time zone,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  is_public boolean DEFAULT false,
  download_count integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT generated_reports_pkey PRIMARY KEY (id),
  CONSTRAINT generated_reports_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis_results(id),
  CONSTRAINT generated_reports_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);
CREATE TABLE public.leads (
  email text NOT NULL UNIQUE,
  name text,
  company text,
  telnr text,
  message text,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  source text NOT NULL DEFAULT 'website'::text,
  additional_data jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT leads_pkey PRIMARY KEY (id)
);
CREATE TABLE public.organizations (
  name character varying NOT NULL,
  domain character varying,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  settings jsonb DEFAULT '{}'::jsonb,
  subscription_tier character varying DEFAULT 'free'::character varying,
  subscription_status character varying DEFAULT 'active'::character varying,
  max_users integer DEFAULT 5,
  max_recordings_per_month integer DEFAULT 50,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT organizations_pkey PRIMARY KEY (id)
);
CREATE TABLE public.recording_sessions (
  user_id uuid NOT NULL,
  description text,
  completed_at timestamp with time zone,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  title text NOT NULL DEFAULT 'Workflow Recording'::text,
  status text NOT NULL DEFAULT 'recording'::text CHECK (status = ANY (ARRAY['recording'::text, 'processing'::text, 'completed'::text, 'failed'::text])),
  duration_seconds integer DEFAULT 0,
  file_size_bytes bigint DEFAULT 0,
  analysis_results jsonb DEFAULT '{}'::jsonb,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  privacy_settings jsonb DEFAULT '{"blur_passwords": true, "exclude_personal_info": false}'::jsonb,
  workflow_type character varying,
  analysis_cost numeric DEFAULT 0.00,
  CONSTRAINT recording_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT recording_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.use_cases (
  title text NOT NULL,
  description text NOT NULL,
  detailed_description text,
  image_url text,
  type text NOT NULL CHECK (type = ANY (ARRAY['product'::text, 'service'::text])),
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  landing_position integer NOT NULL DEFAULT 0,
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT use_cases_pkey PRIMARY KEY (id)
);
CREATE TABLE public.user_profiles (
  id uuid NOT NULL,
  organization_id uuid,
  first_name character varying,
  role character varying DEFAULT 'operator'::character varying,
  settings jsonb DEFAULT '{}'::jsonb,
  last_name character varying,
  job_title character varying,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_profiles_pkey PRIMARY KEY (id),
  CONSTRAINT user_profiles_id_fkey FOREIGN KEY (id) REFERENCES auth.users(id),
  CONSTRAINT user_profiles_organization_id_fkey FOREIGN KEY (organization_id) REFERENCES public.organizations(id)
);
CREATE TABLE public.video_chunks (
  session_id uuid NOT NULL,
  chunk_index integer NOT NULL,
  file_path text,
  file_size_bytes integer,
  error_message text,
  uploaded_at timestamp with time zone,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  upload_status text NOT NULL DEFAULT 'pending'::text CHECK (upload_status = ANY (ARRAY['pending'::text, 'uploading'::text, 'completed'::text, 'failed'::text])),
  retry_count integer DEFAULT 0,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT video_chunks_pkey PRIMARY KEY (id),
  CONSTRAINT video_chunks_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);
CREATE TABLE public.workflow_insights (
  session_id uuid NOT NULL,
  insight_type text NOT NULL,
  title text NOT NULL,
  description text NOT NULL,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  confidence_score numeric DEFAULT 0.0 CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
  time_saved_seconds integer DEFAULT 0,
  roi_score numeric DEFAULT 0.0,
  automation_potential numeric DEFAULT 0.0 CHECK (automation_potential >= 0.0 AND automation_potential <= 1.0),
  priority text DEFAULT 'medium'::text CHECK (priority = ANY (ARRAY['low'::text, 'medium'::text, 'high'::text, 'critical'::text])),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT workflow_insights_pkey PRIMARY KEY (id),
  CONSTRAINT workflow_insights_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);
CREATE TABLE public.workflow_visualizations (
  analysis_id uuid NOT NULL,
  session_id uuid NOT NULL,
  flow_data jsonb NOT NULL,
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  visualization_type character varying DEFAULT 'flow_chart'::character varying,
  layout_algorithm character varying DEFAULT 'dagre'::character varying,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT workflow_visualizations_pkey PRIMARY KEY (id),
  CONSTRAINT workflow_visualizations_analysis_id_fkey FOREIGN KEY (analysis_id) REFERENCES public.analysis_results(id),
  CONSTRAINT workflow_visualizations_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);