from dataclasses import dataclass


@dataclass(frozen=True)
class CreateRecipeForm:
    title: str
    ingredients: str
    glass: str
    instructions: str

    @staticmethod
    def empty() -> "CreateRecipeForm":
        return CreateRecipeForm("", "", "", "")

    def validate(self) -> dict[str, str]:
        # TODO: Add form validation
        return {}
