from fastapi import APIRouter, Depends, HTTPException, Body
from db import get_session
from models.classes import Parameter, Parameter_Main, Tags, New_Response
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Union, Annotated
from starlette import status

parameter_router = APIRouter(tags=[Tags.parameter], prefix="/routers/parameter_router")


@parameter_router.get("/", response_model=Union[list[Parameter_Main], New_Response], tags=[Tags.parameter])
def get_parameters(db: Session = Depends(get_session)):
    parameters = db.query(Parameter).all()
    if parameters is None:
        return JSONResponse(status_code=404, content={"message": "Параметры не найдены"})
    return parameters


@parameter_router.get("/{id_parameter}", response_model=Union[Parameter_Main, New_Response], tags=[Tags.parameter])
def get_parameter(id_parameter: int, db: Session = Depends(get_session)):
    parameter = db.query(Parameter).filter(Parameter.id_parameter == id_parameter).first()
    if parameter is None:
        return JSONResponse(status_code=404, content={"message": "Параметр не найден"})
    return parameter


@parameter_router.post("/", response_model=Union[Parameter_Main, New_Response],
                       tags=[Tags.parameter], status_code=status.HTTP_201_CREATED)
def create_parameter(item: Annotated[Parameter_Main, Body(embed=True, description="Новый параметр")],
                     db: Session = Depends(get_session)):
    try:
        parameter = Parameter(name_parameter=item.name_parameter)
        if parameter is None:
            raise HTTPException(status_code=404, detail="Объект не определен")
        db.add(parameter)
        db.commit()
        db.refresh(parameter)
        return parameter
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Произошла ошибка при добавлении объекта {parameter}")


@parameter_router.put("/", response_model=Union[Parameter_Main, New_Response], tags=[Tags.parameter])
def edit_parameter(item: Annotated[Parameter_Main, Body(embed=True, description="Изменение данных параметра по id")],
                   db: Session = Depends(get_session)):
    parameter = db.query(Parameter).filter(Parameter.id_parameter == item.id_parameter).first()
    if parameter is None:
        return JSONResponse(status_code=404, content={"message": "Параметр не найден"})
    parameter.name_parameter = item.name_parameter
    try:
        db.commit()
        db.refresh(parameter)
    except HTTPException:
        return JSONResponse(status_code=404,
                            content={"message": "Произошла ошибка при изменении объекта {parameter}"})
    return parameter


@parameter_router.delete("/{id_parameter}", response_class=JSONResponse, tags=[Tags.parameter])
def delete_parameter(id_parameter: int, db: Session = Depends(get_session)):
    parameter = db.query(Parameter).filter(Parameter.id_parameter == id_parameter).first()
    if parameter is None:
        return JSONResponse(status_code=404, content={"message": "Параметр не найден"})
    try:
        db.delete(parameter)
        db.commit()
    except HTTPException:
        JSONResponse(content={'message': f'Произошла ошибка при удалении объекта {parameter}'})
    return JSONResponse(content={'message': f'Параметр удален {id_parameter}'})
