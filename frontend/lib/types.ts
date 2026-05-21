export type SourceType = "url" | "raw_html";

export interface Ingredient {
  name: string;
  amount?: string | null;
  unit?: string | null;
  raw_text: string;
}

export interface RecipeStep {
  step_number: number;
  text: string;
  image_url?: string | null;
}

export interface Nutrition {
  calories?: number | null;
  proteins?: number | null;
  fats?: number | null;
  carbohydrates?: number | null;
}

export interface Recipe {
  title?: string | null;
  original_url?: string | null;
  author?: string | null;
  category?: string | null;
  servings?: string | null;
  cooking_time?: string | null;
  image_url?: string | null;
  rating?: string | null;
  description?: string | null;
  ingredients: Ingredient[];
  steps: RecipeStep[];
  nutrition?: Nutrition | null;
  tags: string[];
  equipment: string[];
  comments_count?: number | null;
  source_site: string;
}

export interface HtmlMetrics {
  total_tags: number;
  unique_tags: number;
  total_links: number;
  total_images: number;
  total_text_nodes: number;
  max_dom_depth: number;
  html_size_bytes: number;
  tokens_count: number;
  errors_count: number;
  warnings_count: number;
  recipe_completeness_score: number;
  parser_confidence_score: number;
}

export interface ParserIssue {
  severity: "error" | "warning";
  code: string;
  message: string;
  position?: { line: number; column: number } | null;
}

export interface ParserReport {
  id: string;
  source_type: SourceType;
  source_value: string;
  created_at: string;
  recipe: Recipe;
  html_analysis: HtmlMetrics;
  errors: ParserIssue[];
  warnings: ParserIssue[];
  scores: {
    recipe_completeness_score: number;
    parser_confidence_score: number;
  };
  dom_tree_preview: Record<string, unknown>;
  tokens_preview: Array<Record<string, unknown>>;
}

export interface ReportListItem {
  id: string;
  source_type: SourceType;
  source_value: string;
  recipe_title?: string | null;
  recipe_author?: string | null;
  cooking_time?: string | null;
  ingredients_count: number;
  steps_count: number;
  completeness_score: number;
  confidence_score: number;
  errors_count: number;
  warnings_count: number;
  created_at: string;
}

