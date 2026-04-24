export interface RecipeFormIngredient {
	position: number;
	quantity: string;
	unit: string;
	name: string;
	notes: string;
}

export interface RecipeFormStep {
	position: number;
	text: string;
}

export interface RecipeFormData {
	title: string;
	description: string;
	servings: number | null;
	prep_time_minutes: number | null;
	cook_time_minutes: number | null;
	source_url: string;
	is_public: boolean;
	image_url: string;
	image_public_id: string;
	ingredients: RecipeFormIngredient[];
	steps: RecipeFormStep[];
}

export interface RecipeFormSubmitData
	extends Omit<RecipeFormData, "ingredients"> {
	ingredients: Array<
		Omit<RecipeFormIngredient, "quantity" | "unit" | "notes"> & {
			quantity: string | null;
			unit: string | null;
			notes: string | null;
		}
	>;
}
