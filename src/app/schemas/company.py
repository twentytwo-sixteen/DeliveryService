from pydantic import BaseModel, Field


class AssignCompanyRequest(BaseModel):
    company_id: int = Field(gt=0, description="ID транспортной компании")

