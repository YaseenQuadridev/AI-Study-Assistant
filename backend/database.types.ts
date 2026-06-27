export type Json =
  | string
  | number
  | boolean
  | null
  | { [key: string]: Json | undefined }
  | Json[]

export type Database = {
  __InternalSupabase: {
    PostgrestVersion: "14.5"
  }
  public: {
    Tables: {
      app_state: {
        Row: { key: string; updated_at: string; value: Json }
        Insert: { key: string; updated_at?: string; value?: Json }
        Update: { key?: string; updated_at?: string; value?: Json }
        Relationships: []
      }
      chunks: {
        Row: { created_at: string; document_id: number | null; embedding: string | null; heading: string | null; id: number; text: string; token_count: number | null }
        Insert: { created_at?: string; document_id?: number | null; embedding?: string | null; heading?: string | null; id?: number; text: string; token_count?: number | null }
        Update: { created_at?: string; document_id?: number | null; embedding?: string | null; heading?: string | null; id?: number; text?: string; token_count?: number | null }
        Relationships: [
          { foreignKeyName: "chunks_document_id_fkey"; columns: ["document_id"]; isOneToOne: false; referencedRelation: "documents"; referencedColumns: ["id"] }
        ]
      }
      documents: {
        Row: { created_at: string; filename: string; id: number; markdown: string; status: string }
        Insert: { created_at?: string; filename: string; id?: number; markdown?: string; status?: string }
        Update: { created_at?: string; filename?: string; id?: number; markdown?: string; status?: string }
        Relationships: []
      }
      topics: {
        Row: { created_at: string; d: number; id: number; last_feedback: Json | null; last_studied: number | null; mistakes: number; name: string; p: number; performance_history: Json; s: number; subject: string; u: number; updated_at: string }
        Insert: { created_at?: string; d?: number; id?: number; last_feedback?: Json | null; last_studied?: number | null; mistakes?: number; name: string; p?: number; performance_history?: Json; s?: number; subject?: string; u?: number; updated_at?: string }
        Update: { created_at?: string; d?: number; id?: number; last_feedback?: Json | null; last_studied?: number | null; mistakes?: number; name?: string; p?: number; performance_history?: Json; s?: number; subject?: string; u?: number; updated_at?: string }
        Relationships: []
      }
    }
    Views: { [_ in never]: never }
    Functions: { [_ in never]: never }
    Enums: { [_ in never]: never }
    CompositeTypes: { [_ in never]: never }
  }
}

export type Tables<
  DefaultSchemaTableNameOrOptions extends
    | keyof (Database["public"]["Tables"] & Database["public"]["Views"])
    | { schema: keyof Omit<Database, "__InternalSupabase"> },
  TableName extends DefaultSchemaTableNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
    ? keyof (Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] & Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Views"])
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
  ? (Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Tables"] & Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Views"])[TableName] extends { Row: infer R }
    ? R
    : never
  : DefaultSchemaTableNameOrOptions extends keyof (Database["public"]["Tables"] & Database["public"]["Views"])
    ? (Database["public"]["Tables"] & Database["public"]["Views"])[DefaultSchemaTableNameOrOptions] extends { Row: infer R }
      ? R
      : never
    : never

export type TablesInsert<
  DefaultSchemaTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Omit<Database, "__InternalSupabase"> },
  TableName extends DefaultSchemaTableNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
    ? keyof Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
  ? Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends { Insert: infer I }
    ? I
    : never
  : DefaultSchemaTableNameOrOptions extends keyof Database["public"]["Tables"]
    ? Database["public"]["Tables"][DefaultSchemaTableNameOrOptions] extends { Insert: infer I }
      ? I
      : never
    : never

export type TablesUpdate<
  DefaultSchemaTableNameOrOptions extends
    | keyof Database["public"]["Tables"]
    | { schema: keyof Omit<Database, "__InternalSupabase"> },
  TableName extends DefaultSchemaTableNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
    ? keyof Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Tables"]
    : never = never,
> = DefaultSchemaTableNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
  ? Omit<Database, "__InternalSupabase">[DefaultSchemaTableNameOrOptions["schema"]]["Tables"][TableName] extends { Update: infer U }
    ? U
    : never
  : DefaultSchemaTableNameOrOptions extends keyof Database["public"]["Tables"]
    ? Database["public"]["Tables"][DefaultSchemaTableNameOrOptions] extends { Update: infer U }
      ? U
      : never
    : never

export type Enums<
  DefaultSchemaEnumNameOrOptions extends
    | keyof Database["public"]["Enums"]
    | { schema: keyof Omit<Database, "__InternalSupabase"> },
  EnumName extends DefaultSchemaEnumNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
    ? keyof Omit<Database, "__InternalSupabase">[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"]
    : never = never,
> = DefaultSchemaEnumNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
  ? Omit<Database, "__InternalSupabase">[DefaultSchemaEnumNameOrOptions["schema"]]["Enums"][EnumName]
  : DefaultSchemaEnumNameOrOptions extends keyof Database["public"]["Enums"]
    ? Database["public"]["Enums"][DefaultSchemaEnumNameOrOptions]
    : never

export type CompositeTypes<
  PublicCompositeTypeNameOrOptions extends
    | keyof Database["public"]["CompositeTypes"]
    | { schema: keyof Omit<Database, "__InternalSupabase"> },
  CompositeTypeName extends PublicCompositeTypeNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
    ? keyof Omit<Database, "__InternalSupabase">[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"]
    : never = never,
> = PublicCompositeTypeNameOrOptions extends { schema: keyof Omit<Database, "__InternalSupabase"> }
  ? Omit<Database, "__InternalSupabase">[PublicCompositeTypeNameOrOptions["schema"]]["CompositeTypes"][CompositeTypeName]
  : PublicCompositeTypeNameOrOptions extends keyof Database["public"]["CompositeTypes"]
    ? Database["public"]["CompositeTypes"][PublicCompositeTypeNameOrOptions]
    : never

export const Constants = { public: { Enums: {} } } as const
