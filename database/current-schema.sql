-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.leads (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  email text NOT NULL UNIQUE,
  name text,
  company text,
  telnr text,
  message text,
  source text NOT NULL DEFAULT 'website'::text,
  additional_data jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  CONSTRAINT leads_pkey PRIMARY KEY (id)
);
CREATE TABLE public.recording_sessions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id uuid NOT NULL,
  title text NOT NULL DEFAULT 'Workflow Recording'::text,
  description text,
  status text NOT NULL DEFAULT 'recording'::text CHECK (status = ANY (ARRAY['recording'::text, 'processing'::text, 'completed'::text, 'failed'::text])),
  duration_seconds integer DEFAULT 0,
  file_size_bytes bigint DEFAULT 0,
  analysis_results jsonb DEFAULT '{}'::jsonb,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  completed_at timestamp with time zone,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT recording_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT recording_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES auth.users(id)
);
CREATE TABLE public.use_cases (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  title text NOT NULL,
  description text NOT NULL,
  detailed_description text,
  image_url text,
  landing_position integer NOT NULL DEFAULT 0,
  type text NOT NULL CHECK (type = ANY (ARRAY['product'::text, 'service'::text])),
  is_active boolean NOT NULL DEFAULT true,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT use_cases_pkey PRIMARY KEY (id)
);
CREATE TABLE public.video_chunks (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL,
  chunk_index integer NOT NULL,
  file_path text,
  file_size_bytes integer,
  upload_status text NOT NULL DEFAULT 'pending'::text CHECK (upload_status = ANY (ARRAY['pending'::text, 'uploading'::text, 'completed'::text, 'failed'::text])),
  retry_count integer DEFAULT 0,
  error_message text,
  created_at timestamp with time zone DEFAULT now(),
  uploaded_at timestamp with time zone,
  CONSTRAINT video_chunks_pkey PRIMARY KEY (id),
  CONSTRAINT video_chunks_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.recording_sessions(id)
);
CREATE TABLE public.workflow_insights (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  session_id uuid NOT NULL,
  insight_type text NOT NULL,
  title text NOT NULL,
  description text NOT NULL,
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