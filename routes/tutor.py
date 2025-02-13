from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from models.tutor import Tutor, TutorInDB
from database import get_database

router = APIRouter()

# Create a new tutor
@router.post("/", response_model=TutorInDB)
async def create_tutor(tutor: Tutor, db=Depends(get_database)):
    tutor_dict = tutor.dict()
    result = await db.tutors.insert_one(tutor_dict)
    tutor_dict['id'] = str(result.inserted_id)
    return TutorInDB(**tutor_dict)

# Read all tutors
@router.get("/", response_model=List[TutorInDB])
async def read_tutors(db=Depends(get_database)):
    tutors = await db.tutors.find().to_list(1000)
    return [TutorInDB(**tutor, id=str(tutor['_id'])) for tutor in tutors]

# Read a single tutor by ID
@router.get("/{tutor_id}", response_model=TutorInDB)
async def read_tutor(tutor_id: str, db=Depends(get_database)):
    tutor = await db.tutors.find_one({"_id": ObjectId(tutor_id)})
    if tutor is None:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return TutorInDB(**tutor, id=str(tutor['_id']))

# Update a tutor by ID
@router.put("/{tutor_id}", response_model=TutorInDB)
async def update_tutor(tutor_id: str, tutor: Tutor, db=Depends(get_database)):
    result = await db.tutors.update_one({"_id": ObjectId(tutor_id)}, {"$set": tutor.dict()})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Tutor not found")
    updated_tutor = await db.tutors.find_one({"_id": ObjectId(tutor_id)})
    return TutorInDB(**updated_tutor, id=str(updated_tutor['_id']))

# Delete a tutor by ID
@router.delete("/{tutor_id}", response_model=dict)
async def delete_tutor(tutor_id: str, db=Depends(get_database)):
    result = await db.tutors.delete_one({"_id": ObjectId(tutor_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Tutor not found")
    return {"message": "Tutor deleted successfully"}