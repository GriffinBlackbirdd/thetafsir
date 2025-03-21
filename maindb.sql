-- Create profiles table to store user information
CREATE TABLE profiles (
    id UUID REFERENCES auth.users(id) PRIMARY KEY,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create table to store conversation history
CREATE TABLE conversations (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    question TEXT NOT NULL,
    response TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create table to store conversation history
CREATE TABLE chat_history (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    title TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);

-- Create table to store individual messages within a chat history
CREATE TABLE chat_messages (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    chat_id BIGINT REFERENCES chat_history(id) ON DELETE CASCADE NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
    content TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- Create a table to store user settings and preferences
CREATE TABLE user_settings (
    user_id UUID REFERENCES auth.users(id) PRIMARY KEY,
    language TEXT DEFAULT 'en' NOT NULL,
    theme TEXT DEFAULT 'dark' NOT NULL,
    notification_enabled BOOLEAN DEFAULT true NOT NULL,
    auto_scroll BOOLEAN DEFAULT true NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- Create table to store feedback from users
CREATE TABLE feedback (
    id BIGINT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) NOT NULL,
    conversation_id BIGINT REFERENCES conversations(id) ON DELETE CASCADE,
    rating INTEGER CHECK (rating >= 1 AND rating <= 5),
    feedback_text TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL
);

-- Create a view to get user data with profile information
CREATE VIEW user_profiles AS
SELECT
    au.id,
    au.email,
    p.first_name,
    p.last_name,
    p.created_at,
    au.last_sign_in_at,
    au.confirmed_at
FROM auth.users au
LEFT JOIN profiles p ON au.id = p.id;

-- Set up Row Level Security (RLS) for all tables
-- Profiles table: users can only read and update their own profile
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own profile"
    ON profiles FOR SELECT
    USING (auth.uid() = id);

CREATE POLICY "Users can update own profile"
    ON profiles FOR UPDATE
    USING (auth.uid() = id);

-- Conversations table: users can only access their own conversations
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own conversations"
    ON conversations FOR ALL
    USING (auth.uid() = user_id);

-- Chat history table: users can only access their own chat history
ALTER TABLE chat_history ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own chat history"
    ON chat_history FOR ALL
    USING (auth.uid() = user_id);

-- Chat messages: users can only access messages from their own chats
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can access messages from their chats"
    ON chat_messages FOR ALL
    USING (
        auth.uid() IN (
            SELECT user_id FROM chat_history WHERE id = chat_messages.chat_id
        )
    );

-- User settings: users can only access their own settings
ALTER TABLE user_settings ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own settings"
    ON user_settings FOR ALL
    USING (auth.uid() = user_id);

-- Feedback: users can only manage their own feedback
ALTER TABLE feedback ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can manage own feedback"
    ON feedback FOR ALL
    USING (auth.uid() = user_id);

-- Create a function to handle new user creation
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  -- Create a profile entry for the new user
  INSERT INTO public.profiles (id, first_name, last_name, email, created_at)
  VALUES (
    NEW.id,
    COALESCE(NEW.raw_user_meta_data->>'first_name', 'New'),
    COALESCE(NEW.raw_user_meta_data->>'last_name', 'User'),
    NEW.email,
    NOW()
  );

  -- Create default settings for new user
  INSERT INTO public.user_settings (user_id)
  VALUES (NEW.id);

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Only create the trigger if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_trigger
        WHERE tgname = 'on_auth_user_created'
        AND tgrelid = 'auth.users'::regclass
    ) THEN
        EXECUTE 'CREATE TRIGGER on_auth_user_created
                 AFTER INSERT ON auth.users
                 FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user()';
    END IF;
END$$;

-- Create a function to handle user updates
CREATE OR REPLACE FUNCTION public.handle_user_update()
RETURNS trigger AS $$
BEGIN
  -- Update profile data when user metadata is updated
  UPDATE public.profiles
  SET
    first_name = COALESCE(NEW.raw_user_meta_data->>'first_name', profiles.first_name),
    last_name = COALESCE(NEW.raw_user_meta_data->>'last_name', profiles.last_name),
    updated_at = NOW()
  WHERE id = NEW.id;

  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger to update profile on user update
CREATE TRIGGER on_auth_user_updated
  AFTER UPDATE ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_user_update();

-- Add indexes for better performance
CREATE INDEX idx_conversations_user_id ON conversations (user_id);
CREATE INDEX idx_chat_history_user_id ON chat_history (user_id);
CREATE INDEX idx_chat_messages_chat_id ON chat_messages (chat_id);
CREATE INDEX idx_feedback_user_id ON feedback (user_id);
CREATE INDEX idx_feedback_conversation_id ON feedback (conversation_id);


-- RLS update part
-- Allow insertion into the profiles table during registration
CREATE POLICY "Enable insert for authenticated users only"
ON profiles FOR INSERT
WITH CHECK (auth.uid() = id);

-- Additionally, allow the Supabase service role to insert into profiles
-- This is often needed for the trigger function to work properly
CREATE POLICY "Allow service role to manage profiles"
ON profiles USING (
  (auth.jwt() ->> 'role' = 'service_role'::text)
);
