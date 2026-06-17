from dataclasses import dataclass

from werkzeug.datastructures import ImmutableMultiDict, MultiDict

VALUE_IS_REQUIRED = "Value is required"
MAX_LENGTH = "Maximum length is {0}"
INVALID_VALUE = "Invalid value"

USERNAME_MAX_LENGTH = 20
PASSWORD_MAX_LENGTH = 512
RECIPE_TITLE_MAX_LENGTH = 30
REVIEW_TITLE_MAX_LENGTH = 30
TEXT_MAX_LENGTH = 200
QUERY_MAX_LENGTH = 50


@dataclass(frozen=True)
class LoginForm:
    username: str
    password: str

    @staticmethod
    def empty() -> "LoginForm":
        return LoginForm("", "")

    @staticmethod
    def parse(form: ImmutableMultiDict[str, str]) -> tuple["LoginForm", dict[str, str]]:
        errors: dict[str, str] = {}

        username = form.get("username", default="").strip()
        password = form["password"]

        if not username:
            errors["username"] = VALUE_IS_REQUIRED
        elif len(username) > USERNAME_MAX_LENGTH:
            errors["username"] = MAX_LENGTH.format(USERNAME_MAX_LENGTH)

        if not password:
            errors["password"] = VALUE_IS_REQUIRED
        elif len(password) > PASSWORD_MAX_LENGTH:
            errors["password"] = MAX_LENGTH.format(PASSWORD_MAX_LENGTH)

        return LoginForm(username=username, password=password), errors


@dataclass(frozen=True)
class CreateUserForm:
    username: str
    password1: str
    password2: str

    @staticmethod
    def empty() -> "CreateUserForm":
        return CreateUserForm("", "", "")

    @staticmethod
    def parse(
        form: ImmutableMultiDict[str, str],
    ) -> tuple["CreateUserForm", dict[str, str]]:
        errors: dict[str, str] = {}

        username = form.get("username", default="").strip()
        password1 = form["password1"]
        password2 = form["password2"]

        if not username:
            errors["username"] = VALUE_IS_REQUIRED
        elif len(username) > USERNAME_MAX_LENGTH:
            errors["username"] = MAX_LENGTH.format(USERNAME_MAX_LENGTH)

        if not password1:
            errors["password1"] = VALUE_IS_REQUIRED
        elif len(password1) > PASSWORD_MAX_LENGTH:
            errors["password1"] = MAX_LENGTH.format(PASSWORD_MAX_LENGTH)

        if not password2:
            errors["password2"] = VALUE_IS_REQUIRED
        elif len(password2) > PASSWORD_MAX_LENGTH:
            errors["password2"] = MAX_LENGTH.format(PASSWORD_MAX_LENGTH)
        elif password1 != password2:
            errors["password2"] = "The passwords did not match"

        return (
            CreateUserForm(username=username, password1=password1, password2=password2),
            errors,
        )


@dataclass(frozen=True)
class RecipeForm:
    title: str
    ingredients: str
    instructions: str
    tags: list[int]

    @staticmethod
    def empty() -> "RecipeForm":
        return RecipeForm("", "", "", [])

    @staticmethod
    def parse(
        form: ImmutableMultiDict[str, str], valid_tag_ids: list[int]
    ) -> tuple["RecipeForm", dict[str, str]]:
        errors: dict[str, str] = {}

        title = form.get("title", default="").strip()
        ingredients = form.get("ingredients", default="").strip()
        instructions = form.get("instructions", default="").strip()
        tags = set(form.getlist("tags", type=int))

        if not title:
            errors["title"] = VALUE_IS_REQUIRED
        elif len(title) > RECIPE_TITLE_MAX_LENGTH:
            errors["title"] = MAX_LENGTH.format(RECIPE_TITLE_MAX_LENGTH)

        if not ingredients:
            errors["ingredients"] = VALUE_IS_REQUIRED
        elif len(ingredients) > TEXT_MAX_LENGTH:
            errors["ingredients"] = MAX_LENGTH.format(TEXT_MAX_LENGTH)

        if not instructions:
            errors["instructions"] = VALUE_IS_REQUIRED
        elif len(instructions) > TEXT_MAX_LENGTH:
            errors["instructions"] = MAX_LENGTH.format(TEXT_MAX_LENGTH)

        if not tags.issubset(valid_tag_ids):
            errors["tags"] = INVALID_VALUE

        return (
            RecipeForm(
                title=title,
                ingredients=ingredients,
                instructions=instructions,
                tags=list(tags),
            ),
            errors,
        )


@dataclass(frozen=True)
class RecipeSearchForm:
    query: str
    page: int

    @staticmethod
    def parse(
        args: MultiDict[str, str],
    ) -> tuple["RecipeSearchForm", dict[str, str]]:
        errors: dict[str, str] = {}

        query = args.get("query", default="")
        page = max(1, args.get("page", default=1, type=int))

        if len(query) > QUERY_MAX_LENGTH:
            errors["query"] = MAX_LENGTH.format(QUERY_MAX_LENGTH)

        return RecipeSearchForm(query=query, page=page), errors


@dataclass(frozen=True)
class ReviewForm:
    title: str
    content: str
    rating: int

    @staticmethod
    def empty() -> "ReviewForm":
        return ReviewForm("", "", 0)

    @staticmethod
    def parse(
        form: ImmutableMultiDict[str, str],
    ) -> tuple["ReviewForm", dict[str, str]]:
        errors: dict[str, str] = {}

        title = form.get("title", default="").strip()
        content = form.get("content", default="").strip()
        rating = form.get("rating", default=0, type=int)

        if not title:
            errors["title"] = VALUE_IS_REQUIRED
        elif len(title) > REVIEW_TITLE_MAX_LENGTH:
            errors["title"] = MAX_LENGTH.format(REVIEW_TITLE_MAX_LENGTH)

        if not content:
            errors["content"] = VALUE_IS_REQUIRED
        elif len(content) > TEXT_MAX_LENGTH:
            errors["content"] = MAX_LENGTH.format(TEXT_MAX_LENGTH)

        if not rating:
            errors["rating"] = VALUE_IS_REQUIRED
        elif rating not in [1, 2, 3, 4, 5]:
            errors["rating"] = INVALID_VALUE

        return ReviewForm(title=title, content=content, rating=rating), errors
