from pydantic import BaseModel, Field, model_validator
from typing import Optional, List


class Period(BaseModel):
    start: Optional[str] = None
    end: Optional[str] = None


class Address(BaseModel):
    use: Optional[str] = Field(None, description="home | work | temp | old | billing - purpose of this address")
    type: Optional[str] = Field(None, description="postal | physical | both")
    text: Optional[str] = Field(None, description="Text representation of the address")
    line: Optional[List[str]] = Field(None, description="Street name, number, direction & P.O. Box etc.")
    city: Optional[str] = Field(None, description="Name of city, town etc.")
    district: Optional[str] = Field(None, description="District name (aka county)")
    state: Optional[str] = Field(None, description="Sub-unit of country (abbreviations ok)")
    postalCode: Optional[str] = Field(None, description="Postal code for area")
    country: Optional[str] = Field(None, description="Country (e.g. may be ISO 3166 2 or 3 letter code)")
    period: Optional[Period] = Field(None, description="Time period when address was/is in use")

    @model_validator(mode="before")
    def custom_mapper(cls, values):
        extensions = values.get("extension", [])
        if extensions:
            address_extensions = extensions[0].get("extension", [])
            values["line"] = []
            for extension in address_extensions:
                value_string = extension.get("valueString", "")
                if value_string:
                    values["line"].append(value_string)
        return values


class HumanName(BaseModel):
    use: Optional[str] = Field(None, description="usual | official | temp | nickname | anonymous | old | maiden")
    text: Optional[str] = Field(None, description="Text representation of the full name")
    family: Optional[str] = Field(None, description="Family name (often called 'Surname')")
    given: Optional[List[str]] = Field(None, description="Given names (not always 'first'). Includes middle names")
    prefix: Optional[List[str]] = Field(None, description="Parts that come before the name")
    suffix: Optional[List[str]] = Field(None, description="Parts that come after the name")
    period: Optional[Period] = Field(None, description="Time period when name was/is in use")


class Patient(BaseModel):
    patient_id: str = Field(alias="id")
    identifier: str = Field(description="An identifier for this patient")
    active: bool = Field(description="Whether this patient's record is in active use")
    name: HumanName = Field(description="A name associated with the patient")
    gender: str = Field(description="male | female | other | unknown")
    birth_date: str = Field(alias="birthDate", description="The date of birth for the individual")
    deceased: bool = Field(alias="deceasedBoolean", description="Indicates if the individual is deceased or not")
    address: Optional[List[Address]] = Field(description="Addresses for the individual")

    @model_validator(mode="before")
    def custom_mapper(cls, values):
        meta = values.get("meta", {})
        values["version_id"] = meta.get("versionId")
        values["last_updated"] = meta.get("lastUpdated")
        identifiers = values.get("identifier", [])
        if identifiers:
            values["identifier"] = identifiers[0].get("value")
        name = values.get("name", [])
        if isinstance(name, list) and name:
            values["name"] = HumanName(**name[0])
        elif isinstance(name, dict):
            values["name"] = HumanName(**name)
        addresses = values.get("address", [])
        if addresses != []:
            values["address"] = [Address(**address) if isinstance(address, dict) else address for address in addresses]
        return values


class Coding(BaseModel):
    system: Optional[str] = None
    code: Optional[str] = None
    display: Optional[str] = None


class CodeableConcept(BaseModel):
    coding: Optional[List[Coding]] = None
    text: Optional[str] = None


class Reference(BaseModel):
    reference: Optional[str] = None
    type: Optional[str] = None
    display: Optional[str] = None


class Quantity(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None
    system: Optional[str] = None
    code: Optional[str] = None


class ReferenceRange(BaseModel):
    low: Optional[Quantity] = None
    high: Optional[Quantity] = None


class ObservationResource(BaseModel):
    id: Optional[str] = Field(None, description="The logical id of the resource.")
    status: Optional[str] = Field(None, description="The status of the result value.")
    category: Optional[List[Coding]] = Field(
        None, description="A code that classifies the general type of observation being made."
    )
    code: Optional[CodeableConcept] = Field(
        ..., description="Describes what was observed. Sometimes this is called the observation 'name'."
    )
    subject: Optional[Reference] = Field(
        None,
        description="The patient this observation is about and into whose record the observation is placed.",
    )
    encounter: Optional[Reference] = Field(
        None, description="The healthcare event during which this observation is made."
    )
    effectiveDateTime: Optional[str] = Field(
        None, description="The time or time-period the observed value is asserted as being true."
    )
    issued: Optional[str] = Field(
        None, description="The date and time this version of the observation was made available to providers."
    )
    valueQuantity: Optional[Quantity] = Field(
        None, description="The information determined as a result of making the observation."
    )
    referenceRange: Optional[List[ReferenceRange]] = Field(
        None, description="Guidance on how to interpret the value by comparison to a normal or recommended range."
    )

    @model_validator(mode="before")
    def custom_mapper(cls, values):
        category = values.get("category", [])
        if category:
            values["category"] = [Coding(**item) for item in category]

        code = values.get("code", {})
        if isinstance(code, dict):
            values["code"] = CodeableConcept(**code)

        return values


class ClinicalStatusCoding(BaseModel):
    code: Optional[str] = Field(
        None, description="active | recurrence | relapse | inactive | remission | resolved | unknown"
    )
    system: Optional[str] = None
    text: Optional[str] = Field(None, description="Plain text representation of the concept")


class ConditionCode(BaseModel):
    text: Optional[str] = None


class Recorder(BaseModel):
    reference: Optional[str] = Field(None, description="A reference from one resource to another")
    type: Optional[str] = Field(None, description="Type of resource being referenced")
    display: Optional[str] = Field(None, description="Plain text alternative for the resource")


class ConditionResource(BaseModel):
    id: Optional[str] = Field(None, description="External Ids for this condition")
    status: Optional[ClinicalStatusCoding] = Field(None, description="The status of the result value.")
    code: Optional[CodeableConcept] = Field(..., description="Identification of the condition, problem or diagnosis")
    subject: Optional[Reference] = Field(None, description="Who has the condition?")
    onsetDateTime: Optional[str] = Field(None, description="Estimated or actual date, date-time, or age")
    recordedDate: Optional[str] = Field(None, description="Date condition was first recorded")
    recorder: Optional[Recorder] = Field(None, description="Who recorded the condition")

    @model_validator(mode="before")
    def custom_mapper(cls, values):
        code = values.get("code", {})
        if isinstance(code, dict):
            values["code"] = CodeableConcept(**code)
        return values


class Substance(BaseModel):
    coding: Optional[List[Coding]]
    text: Optional[str]


class Manifestation(BaseModel):
    coding: Optional[List[Coding]]
    text: Optional[str]


class AllergyIntolerance(BaseModel):
    substance: Optional[Substance]
    manifestation: Optional[List[Manifestation]]
    severity: Optional[str]


class AllergyIntoleranceResource(BaseModel):
    id: Optional[str] = Field(None, description="External ids for this item")
    clinicalStatus: Optional[CodeableConcept] = Field(None, description="The status of the result value.")
    verificationStatus: Optional[CodeableConcept] = Field(
        None, description="unconfirmed | presumed | confirmed | refuted | entered-in-error"
    )
    type: Optional[str] = Field(None, description="allergy | intolerance - Underlying mechanism (if known)")
    category: Optional[List[str]] = Field(None, description="food | medication | environment | biologic")
    criticality: Optional[str] = Field(None, description="low | high | unable-to-assess")
    code: Optional[CodeableConcept] = Field(..., description="Identification of the condition, problem or diagnosis")
    patient: Optional[Reference] = Field(None, description="Who the allergy or intolerance is for")
    recordedDate: Optional[str] = Field(None, description="Date condition was first recorded")
    recorder: Optional[Recorder] = Field(None, description="Who recorded the condition")
    reaction: List[AllergyIntolerance] = Field(
        None, description="Adverse Reaction Events linked to exposure to substance"
    )


class PatientContext(BaseModel):
    patient: Optional[Patient]
    observations: Optional[List[ObservationResource]] = []
    conditions: Optional[List[ConditionResource]] = []
    allergies: Optional[List[AllergyIntoleranceResource]] = []
