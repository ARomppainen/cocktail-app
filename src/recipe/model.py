from dataclasses import dataclass


@dataclass(frozen=True)
class Recipe:
    id: str
    user_id: str
    created_at: str
    title: str
    ingredients: str
    glass: str
    instructions: str


@dataclass(frozen=True)
class RecipeForm:
    title: str
    ingredients: str
    glass: str
    instructions: str

    @staticmethod
    def empty() -> "RecipeForm":
        return RecipeForm("", "", "", "")

    def validate(self) -> dict[str, str]:
        errors: dict[str, str] = {}

        if not self.title:
            errors["title"] = "Value is required"

        if not self.ingredients:
            errors["ingredients"] = "Value is required"

        if not self.glass:
            errors["glass"] = "Value is required"

        if not self.instructions:
            errors["instructions"] = "Value is required"

        return errors
