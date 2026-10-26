from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.api.deps import get_db, get_current_user, get_current_user_optional
from app.models.user import User, UserProfile
from app.models.cooking import SavedRecipe
from app.schemas.cooking import RecipeGenerateRequest, RecipeChatRequest, SavedRecipeCreate, RecipeResponse
from app.services.ai.provider_factory import get_ai_provider

router = APIRouter(prefix="/cooking", tags=["Smart Cooking Assistant"])


@router.post("/recipes", response_model=dict)
async def generate_cooking_recipe(
    req: RecipeGenerateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db)
):
    """
    Generates a recipe based on ingredients, dietary preferences, cuisine, and serving counts.
    """
    dietary_restrictions = list(req.dietary_restrictions)
    
    # Merge user profile restrictions if logged in
    if current_user:
        profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
        if profile:
            if profile.dietary_pattern and profile.dietary_pattern != "omnivore":
                dietary_restrictions.append(profile.dietary_pattern)
            if profile.allergies:
                dietary_restrictions.extend([f"Allergic to {a}" for a in profile.allergies])
            if profile.restrictions:
                dietary_restrictions.extend(profile.restrictions)

    ai_provider = get_ai_provider()
    try:
        recipe_data = await ai_provider.generate_recipe(
            query=req.query,
            ingredients=req.ingredients,
            dietary_restrictions=list(set(dietary_restrictions)),
            cuisine=req.cuisine,
            servings=req.servings,
            cooking_time=req.cooking_time_min
        )
        return recipe_data
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Recipe generation error: {str(e)}"
        )


@router.post("/chat", response_model=dict)
async def cooking_chat(
    req: RecipeChatRequest,
    current_user: Optional[User] = Depends(get_current_user_optional)
):
    """
    Handles follow-up culinary questions (e.g. 'Make this higher in protein', 'What can I substitute for garlic?').
    """
    ai_provider = get_ai_provider()
    context = "You are a professional chef assisting with cooking and recipe adjustments.\n"
    if req.current_recipe:
        context += f"Current Active Recipe Context:\nTitle: {req.current_recipe.get('title')}\n"
        context += f"Ingredients: {req.current_recipe.get('ingredients')}\n"
        context += f"Instructions: {req.current_recipe.get('instructions')}\n"

    messages = list(req.conversation_history)
    messages.append({"role": "user", "content": req.message})

    try:
        reply = await ai_provider.chat(messages=messages, context=context)
        return {"reply": reply}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Culinary assistant error: {str(e)}"
        )


@router.post("/save", response_model=RecipeResponse, status_code=status.HTTP_201_CREATED)
def save_recipe(
    recipe_in: SavedRecipeCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_recipe = SavedRecipe(
        user_id=current_user.id,
        title=recipe_in.title,
        description=recipe_in.description,
        prep_time_min=recipe_in.prep_time_min,
        cook_time_min=recipe_in.cook_time_min,
        servings=recipe_in.servings,
        cuisine=recipe_in.cuisine,
        difficulty=recipe_in.difficulty,
        ingredients=recipe_in.ingredients,
        instructions=recipe_in.instructions,
        substitutions=recipe_in.substitutions,
        allergens=recipe_in.allergens,
        estimated_nutrition=recipe_in.estimated_nutrition,
        food_safety_notes=recipe_in.food_safety_notes
    )
    db.add(db_recipe)
    db.commit()
    db.refresh(db_recipe)
    return db_recipe


@router.get("/recipes", response_model=List[RecipeResponse])
def get_saved_recipes(
    search: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(SavedRecipe).filter(SavedRecipe.user_id == current_user.id)
    if search:
        query = query.filter(SavedRecipe.title.ilike(f"%{search}%"))
    return query.order_by(SavedRecipe.created_at.desc()).all()


@router.get("/recipes/{recipe_id}", response_model=RecipeResponse)
def get_recipe_detail(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recipe = db.query(SavedRecipe)\
        .filter(SavedRecipe.id == recipe_id, SavedRecipe.user_id == current_user.id)\
        .first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found.")
    return recipe


@router.delete("/recipes/{recipe_id}", status_code=status.HTTP_200_OK)
def delete_recipe(
    recipe_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    recipe = db.query(SavedRecipe)\
        .filter(SavedRecipe.id == recipe_id, SavedRecipe.user_id == current_user.id)\
        .first()
    if not recipe:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Recipe not found or unauthorized.")
    db.delete(recipe)
    db.commit()
    return {"message": "Recipe removed successfully."}
