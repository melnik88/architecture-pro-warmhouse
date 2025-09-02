from fastapi import FastAPI, HTTPException, Depends, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from fastapi.openapi.utils import get_openapi
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="Теперь умный дом API",
    description="REST API для платформы Теперь умный дом",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1}
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    # Удаляем только из документации (реальный ответ 422 остаётся)
    for path in openapi_schema.get("paths", {}).values():
        for method in path.values():
            responses = method.get("responses", {})
            if "422" in responses:
                del responses["422"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


# Security
security = HTTPBearer()

# Enums
class DeviceType(str, Enum):
    temperature = "temperature"
    humidity = "humidity"
    motion = "motion"
    thermostat = "thermostat"

class DeviceStatus(str, Enum):
    online = "online"
    offline = "offline"
    error = "error"

# Base Models
class ErrorResponse(BaseModel):
    error: Dict[str, Any] = Field(..., example={
        "code": "VALIDATION_ERROR",
        "message": "Invalid input data",
        "details": {}
    })

class MessageResponse(BaseModel):
    message: str

class PaginationInfo(BaseModel):
    page: int = Field(..., ge=1)
    limit: int = Field(..., ge=1, le=100)
    total: int = Field(..., ge=0)
    pages: int = Field(..., ge=0)

# Authentication Models
class LoginRequest(BaseModel):
    username: str = Field(..., example="user@example.com")
    password: str = Field(..., example="password123")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600

class SessionInfo(BaseModel):
    session_id: str = Field(..., example=str(uuid.uuid4()))
    user_id: str = Field(..., example=str(uuid.uuid4()))
    created_at: datetime
    expires_at: datetime

# User Models
class User(BaseModel):
    user_id: str = Field(..., example=str(uuid.uuid4()))
    username: str = Field(..., example="user@example.com")
    created_at: datetime

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, example="newuser@example.com")

# Device Models
class DeviceBase(BaseModel):
    device_name: str = Field(..., example="Датчик температуры гостиной")
    device_type: DeviceType = Field(..., example=DeviceType.temperature)
    configuration: Optional[Dict[str, Any]] = Field(default={}, example={"min_temp": 18, "max_temp": 25})

class DeviceCreate(DeviceBase):
    home_id: str = Field(..., example=str(uuid.uuid4()), description="ID дома для установки устройства")

class DeviceUpdate(BaseModel):
    device_name: Optional[str] = Field(None, example="Обновленное название устройства")
    device_type: Optional[DeviceType] = None
    status: Optional[DeviceStatus] = None
    configuration: Optional[Dict[str, Any]] = None

class DeviceBindRequest(BaseModel):
    home_id: str = Field(..., example=str(uuid.uuid4()), description="ID дома для привязки устройства")

class ScenarioBindRequest(BaseModel):
    home_id: str = Field(..., example=str(uuid.uuid4()), description="ID дома для привязки сценария")

class Device(DeviceBase):
    device_id: str = Field(..., example=str(uuid.uuid4()))
    home_id: str = Field(..., example=str(uuid.uuid4()))
    status: DeviceStatus = Field(..., example=DeviceStatus.online)
    created_at: datetime

class DeviceListResponse(BaseModel):
    data: List[Device]
    pagination: PaginationInfo

# Telemetry Models
class Telemetry(BaseModel):
    telemetry_id: str = Field(..., example=str(uuid.uuid4()))
    device_id: str = Field(..., example=str(uuid.uuid4()))
    telemetry_data: List[Dict[str, Any]] = Field(..., example=[
        {
            "metric": "temperature",
            "value": 23.5,
            "unit": "°C",
            "sensor_id": "temp_001"
        },
        {
            "metric": "humidity",
            "value": 45.2,
            "unit": "%",
            "sensor_id": "hum_001"
        }
    ])
    timestamp: datetime

class TelemetryListResponse(BaseModel):
    data: List[Telemetry]
    pagination: PaginationInfo

# Scenario Models
class ScenarioAction(BaseModel):
    action: str = Field(..., example="set_temperature", description="Действие которое должно выполнить устройство")
    device_id: str = Field(..., example=str(uuid.uuid4()), description="ID устройства которое должно выполнить действие")
    condition: Optional[Dict[str, Any]] = Field(None, example={
        "metric": "temperature",
        "operator": "<",
        "value": 20
    }, description="Условие при котором должно выполниться действие")
    parameters: Optional[Dict[str, Any]] = Field(default={}, example={
        "target_value": 22,
        "duration": 300
    }, description="Параметры для выполнения действия")

class ScenarioBase(BaseModel):
    scenario_title: str = Field(..., example="Утренний режим")
    actions: List[ScenarioAction] = Field(..., example=[
        {
            "action": "set_temperature",
            "device_id": str(uuid.uuid4()),
            "condition": {
                "metric": "temperature",
                "operator": "<",
                "value": 20
            },
            "parameters": {
                "target_value": 22,
                "duration": 300
            }
        }
    ])
    is_active: bool = Field(default=True, example=True)

class ScenarioCreate(ScenarioBase):
    home_id: str = Field(..., example=str(uuid.uuid4()), description="ID дома для создания сценария")

class ScenarioUpdate(BaseModel):
    scenario_title: Optional[str] = Field(None, example="Обновленный сценарий")
    actions: Optional[List[ScenarioAction]] = None
    is_active: Optional[bool] = None

class Scenario(ScenarioBase):
    scenario_id: str = Field(..., example=str(uuid.uuid4()))
    home_id: str = Field(..., example=str(uuid.uuid4()))
    created_at: datetime

class ScenarioListResponse(BaseModel):
    data: List[Scenario]
    pagination: PaginationInfo

class ScenarioExecutionResponse(BaseModel):
    message: str = "Scenario executed successfully"
    execution_id: str = Field(..., example=str(uuid.uuid4()))

# DeviceScenario Models (Many-to-Many relationship)
class DeviceScenario(BaseModel):
    device_scenario_id: str = Field(..., example=str(uuid.uuid4()))
    device_id: str = Field(..., example=str(uuid.uuid4()))
    scenario_id: str = Field(..., example=str(uuid.uuid4()))
    created_at: datetime

# Home Models
class HomeBase(BaseModel):
    home_name: str = Field(..., example="Мой дом")
    address: str = Field(..., example="ул. Примерная, 123")

class HomeCreate(HomeBase):
    pass

class HomeUpdate(BaseModel):
    home_name: Optional[str] = Field(None, example="Обновленное название")
    address: Optional[str] = Field(None, example="ул. Новая, 456")

class Home(HomeBase):
    home_id: str = Field(..., example=str(uuid.uuid4()))
    owner_id: str = Field(..., example=str(uuid.uuid4()))
    devices: List[Device] = Field(default=[], description="Устройства в доме")
    scenarios: List[Scenario] = Field(default=[], description="Сценарии дома")
    created_at: datetime

class HomeListResponse(BaseModel):
    data: List[Home]
    pagination: PaginationInfo

# Dependency for authentication
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """
    Dependency для получения текущего пользователя из JWT токена
    В реальном приложении здесь будет валидация JWT токена
    """
    # Проверка валидности токена (mock логика для демонстрации)
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "MISSING_TOKEN", "message": "Authorization token is required", "details": {}}}
        )

    # Пример проверки невалидного токена
    if credentials.credentials == "invalid_token":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": {"code": "INVALID_SESSION", "message": "Session is invalid or expired", "details": {}}}
        )

    # Mock user for demonstration
    return User(
        user_id=str(uuid.uuid4()),
        username="user@example.com",
        created_at=datetime.now()
    )

# Authentication Endpoints
@app.post("/auth/login",
          response_model=TokenResponse,
          summary="Вход в систему",
          description="Аутентификация пользователя и получение JWT токена",
          tags=["🔐 Аутентификация"],
          responses={
              200: {"model": TokenResponse, "description": "Успешная аутентификация"},
              401: {"model": ErrorResponse, "description": "Неверные учетные данные"},
          })
async def login(login_data: LoginRequest):
    """
    Вход пользователя в систему

    Проверяет учетные данные пользователя и возвращает JWT токен при успешной аутентификации.
    При неверных учетных данных возвращает статус 401 Unauthorized.
    """
    # В реальном приложении здесь будет проверка учетных данных
    if login_data.username == "user@example.com" and login_data.password == "password123":
        return TokenResponse(
            access_token="mock_jwt_token_here",
            token_type="bearer",
            expires_in=3600
        )
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"error": {"code": "INVALID_CREDENTIALS", "message": "Неверные учетные данные", "details": {}}}
    )

@app.post("/auth/logout",
          response_model=MessageResponse,
          summary="Выход из системы",
          description="Завершение пользовательской сессии",
          tags=["🔐 Аутентификация"])
async def logout(current_user: User = Depends(get_current_user)):
    """Выход из системы"""
    return MessageResponse(message="Successfully logged out")

@app.get("/auth/session",
         response_model=SessionInfo,
         summary="Информация о сессии",
         description="Получение информации о текущей пользовательской сессии",
         tags=["🔐 Аутентификация"],
         responses={
             200: {"model": SessionInfo, "description": "Информация о сессии успешно получена"},
             401: {"model": ErrorResponse, "description": "Сессия невалидна или истекла"}
         })
async def get_session_info(current_user: User = Depends(get_current_user)):
    """
    Получение информации о текущей сессии

    Возвращает информацию о текущей пользовательской сессии.
    При невалидной или истекшей сессии возвращает статус 401 Unauthorized.
    """
    from datetime import timedelta
    return SessionInfo(
        session_id=str(uuid.uuid4()),
        user_id=current_user.user_id,
        created_at=datetime.now() - timedelta(hours=1),
        expires_at=datetime.now() + timedelta(hours=23)
    )


# User Endpoints
@app.get("/profile",
         response_model=User,
         summary="Получение профиля пользователя",
         description="Получение информации о текущем пользователе",
         tags=["👤 Пользователи"],
         responses={
             200: {"model": User, "description": "Профиль пользователя успешно получен"},
             404: {"model": ErrorResponse, "description": "Пользователь не найден"}
         })
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """
    Получение профиля текущего пользователя

    Возвращает информацию о текущем аутентифицированном пользователе.
    При отсутствии пользователя в системе возвращает 404.
    """
    # В реальном приложении здесь может быть дополнительная проверка существования пользователя в БД
    if not current_user or not current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "Пользователь не найден", "details": {}}}
        )
    return current_user

@app.put("/profile",
         response_model=User,
         summary="Обновление профиля пользователя",
         description="Обновление информации о текущем пользователе",
         tags=["👤 Пользователи"],
         responses={
             200: {"model": User, "description": "Профиль пользователя успешно обновлен"},
             404: {"model": ErrorResponse, "description": "Пользователь не найден"}
         })
async def update_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user)
):
    """
    Обновление профиля пользователя

    Обновляет информацию о текущем аутентифицированном пользователе.
    При отсутствии пользователя в системе возвращает 404.
    """
    # В реальном приложении здесь может быть дополнительная проверка существования пользователя в БД
    if not current_user or not current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "USER_NOT_FOUND", "message": "Пользователь не найден", "details": {}}}
        )

    # В реальном приложении здесь будет обновление в базе данных
    updated_user = current_user.copy()
    if user_update.username:
        updated_user.username = user_update.username
    return updated_user

# Home Endpoints
@app.get("/homes",
         response_model=HomeListResponse,
         summary="Получение списка домов",
         description="Получение всех домов пользователя с пагинацией",
         tags=["🏠 Дома"],
         responses={
            404: {"model": ErrorResponse, "description": "Списка домов нет"}
            }
         )
async def get_homes(
    page: int = Query(1, ge=1, description="Номер страницы"),
    limit: int = Query(20, ge=1, le=100, description="Количество элементов на странице"),
    current_user: User = Depends(get_current_user)
):
    """Получение списка домов пользователя"""
    # Mock data
    mock_device = Device(
        device_id=str(uuid.uuid4()),
        home_id=str(uuid.uuid4()),
        device_name="Датчик температуры гостиной",
        device_type=DeviceType.temperature,
        status=DeviceStatus.online,
        configuration={"min_temp": 18, "max_temp": 25},
        created_at=datetime.now()
    )

    mock_scenario = Scenario(
        scenario_id=str(uuid.uuid4()),
        home_id=str(uuid.uuid4()),
        scenario_title="Утренний режим",
        actions=[
            ScenarioAction(
                action="set_temperature",
                device_id=str(uuid.uuid4()),
                condition={
                    "metric": "temperature",
                    "operator": "<",
                    "value": 20
                },
                parameters={
                    "target_value": 22,
                    "duration": 300
                }
            )
        ],
        is_active=True,
        created_at=datetime.now()
    )

    mock_homes = [
        Home(
            home_id=str(uuid.uuid4()),
            owner_id=current_user.user_id,
            home_name="Мой дом",
            address="ул. Примерная, 123",
            devices=[mock_device],
            scenarios=[mock_scenario],
            created_at=datetime.now()
        )
    ]

    return HomeListResponse(
        data=mock_homes,
        pagination=PaginationInfo(page=page, limit=limit, total=1, pages=1)
    )

@app.post("/homes",
          response_model=Home,
          status_code=status.HTTP_201_CREATED,
          summary="Создание нового дома",
          description="Добавление нового дома для пользователя",
          tags=["🏠 Дома"])
async def create_home(
    home_data: HomeCreate,
    current_user: User = Depends(get_current_user)
):
    """Создание нового дома"""
    return Home(
        home_id=str(uuid.uuid4()),
        owner_id=current_user.user_id,
        home_name=home_data.home_name,
        address=home_data.address,
        devices=[],
        scenarios=[],
        created_at=datetime.now()
    )

@app.get("/homes/{home_id}",
         response_model=Home,
         summary="Получение информации о доме",
         description="Получение детальной информации о конкретном доме",
         tags=["🏠 Дома"],
         responses={404: {"model": ErrorResponse, "description": "Дом не найден"}})
async def get_home(
    home_id: str,
    current_user: User = Depends(get_current_user)
):
    """Получение информации о конкретном доме"""
    # В реальном приложении здесь будет поиск в базе данных
    mock_device = Device(
        device_id=str(uuid.uuid4()),
        home_id=home_id,
        device_name="Датчик температуры гостиной",
        device_type=DeviceType.temperature,
        status=DeviceStatus.online,
        configuration={"min_temp": 18, "max_temp": 25},
        created_at=datetime.now()
    )

    mock_scenario = Scenario(
        scenario_id=str(uuid.uuid4()),
        home_id=home_id,
        scenario_title="Утренний режим",
        actions=[
            ScenarioAction(
                action="set_temperature",
                device_id=str(uuid.uuid4()),
                condition={
                    "metric": "temperature",
                    "operator": "<",
                    "value": 20
                },
                parameters={
                    "target_value": 22,
                    "duration": 300
                }
            )
        ],
        is_active=True,
        created_at=datetime.now()
    )

    return Home(
        home_id=home_id,
        owner_id=current_user.user_id,
        home_name="Мой дом",
        address="ул. Примерная, 123",
        devices=[mock_device],
        scenarios=[mock_scenario],
        created_at=datetime.now()
    )

@app.put("/homes/{home_id}",
         response_model=Home,
         summary="Обновление информации о доме",
         description="Изменение данных дома",
         tags=["🏠 Дома"])
async def update_home(
    home_id: str,
    home_update: HomeUpdate,
    current_user: User = Depends(get_current_user)
):
    """Обновление информации о доме"""
    # Mock updated home
    mock_device = Device(
        device_id=str(uuid.uuid4()),
        home_id=home_id,
        device_name="Датчик температуры гостиной",
        device_type=DeviceType.temperature,
        status=DeviceStatus.online,
        configuration={"min_temp": 18, "max_temp": 25},
        created_at=datetime.now()
    )

    mock_scenario = Scenario(
        scenario_id=str(uuid.uuid4()),
        home_id=home_id,
        scenario_title="Утренний режим",
        actions=[
            ScenarioAction(
                action="set_temperature",
                device_id=str(uuid.uuid4()),
                condition={
                    "metric": "temperature",
                    "operator": "<",
                    "value": 20
                },
                parameters={
                    "target_value": 22,
                    "duration": 300
                }
            )
        ],
        is_active=True,
        created_at=datetime.now()
    )

    return Home(
        home_id=home_id,
        owner_id=current_user.user_id,
        home_name=home_update.home_name or "Мой дом",
        address=home_update.address or "ул. Примерная, 123",
        devices=[mock_device],
        scenarios=[mock_scenario],
        created_at=datetime.now()
    )

@app.delete("/homes/{home_id}",
           response_model=MessageResponse,
           summary="Удаление дома",
           description="Удаление дома и всех связанных устройств",
           tags=["🏠 Дома"])
async def delete_home(
    home_id: str,
    current_user: User = Depends(get_current_user)
):
    """Удаление дома"""
    return MessageResponse(message="Home deleted successfully")

# Device Endpoints
@app.post("/devices",
          response_model=Device,
          status_code=status.HTTP_201_CREATED,
          summary="Создание устройства",
          description="Создание нового устройства с привязкой к дому",
          tags=["🔌 Устройства"])
async def create_device(
    device_data: DeviceCreate,
    current_user: User = Depends(get_current_user)
):
    """Создание нового устройства с привязкой к указанному дому"""
    return Device(
        device_id=str(uuid.uuid4()),
        home_id=device_data.home_id,
        device_name=device_data.device_name,
        device_type=device_data.device_type,
        status=DeviceStatus.online,  # Online после привязки к дому
        configuration=device_data.configuration or {},
        created_at=datetime.now()
    )

@app.get("/devices/{device_id}",
         response_model=Device,
         summary="Получение информации об устройстве",
         description="Получение детальной информации об устройстве",
         tags=["🔌 Устройства"])
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """Получение информации об устройстве"""
    return Device(
        device_id=device_id,
        home_id=str(uuid.uuid4()),
        device_name="Датчик температуры гостиной",
        device_type=DeviceType.temperature,
        status=DeviceStatus.online,
        configuration={"min_temp": 18, "max_temp": 25},
        created_at=datetime.now()
    )

@app.put("/devices/{device_id}",
         response_model=Device,
         summary="Обновление устройства",
         description="Изменение настроек и параметров устройства",
         tags=["🔌 Устройства"])
async def update_device(
    device_id: str,
    device_update: DeviceUpdate,
    current_user: User = Depends(get_current_user)
):
    """Обновление устройства"""
    return Device(
        device_id=device_id,
        home_id=str(uuid.uuid4()),
        device_name=device_update.device_name or "Датчик температуры гостиной",
        device_type=device_update.device_type or DeviceType.temperature,
        status=device_update.status or DeviceStatus.online,
        configuration=device_update.configuration or {"min_temp": 18, "max_temp": 25},
        created_at=datetime.now()
    )

@app.delete("/devices/{device_id}",
           response_model=MessageResponse,
           summary="Удаление устройства",
           description="Удаление устройства из системы",
           tags=["🔌 Устройства"])
async def delete_device(
    device_id: str,
    current_user: User = Depends(get_current_user)
):
    """Удаление устройства"""
    return MessageResponse(message="Device deleted successfully")

# Telemetry Endpoints
@app.get("/telemetry/{device_id}",
         response_model=TelemetryListResponse,
         summary="Получение телеметрии устройства",
         description="Получение телеметрических данных устройства за период",
         tags=["📊 Телеметрия"])
async def get_device_telemetry(
    device_id: str,
    start_date: Optional[datetime] = Query(None, description="Начальная дата (ISO 8601)"),
    end_date: Optional[datetime] = Query(None, description="Конечная дата (ISO 8601)"),
    page: int = Query(1, ge=1),
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user)
):
    """Получение телеметрических данных устройства"""
    mock_telemetry = [
        Telemetry(
            telemetry_id=str(uuid.uuid4()),
            device_id=device_id,
            telemetry_data=[
                {
                    "metric": "temperature",
                    "value": 23.5,
                    "unit": "°C",
                    "sensor_id": "temp_001"
                },
                {
                    "metric": "humidity",
                    "value": 45.2,
                    "unit": "%",
                    "sensor_id": "hum_001"
                }
            ],
            timestamp=datetime.now()
        )
    ]

    return TelemetryListResponse(
        data=mock_telemetry,
        pagination=PaginationInfo(page=page, limit=limit, total=1, pages=1)
    )


# Scenario Endpoints
@app.post("/scenarios",
          response_model=Scenario,
          status_code=status.HTTP_201_CREATED,
          summary="Создание сценария",
          description="Создание нового сценария автоматизации",
          tags=["⚙️ Сценарии"])
async def create_scenario(
    scenario_data: ScenarioCreate,
    current_user: User = Depends(get_current_user)
):
    """Создание нового сценария"""
    return Scenario(
        scenario_id=str(uuid.uuid4()),
        home_id=scenario_data.home_id,  # Используем home_id из запроса
        scenario_title=scenario_data.scenario_title,
        actions=scenario_data.actions,
        is_active=scenario_data.is_active,
        created_at=datetime.now()
    )

@app.get("/scenarios/{scenario_id}",
         response_model=Scenario,
         summary="Получение информации о сценарии",
         description="Получение детальной информации о сценарии",
         tags=["⚙️ Сценарии"])
async def get_scenario(
    scenario_id: str,
    current_user: User = Depends(get_current_user)
):
    """Получение информации о сценарии"""
    return Scenario(
        scenario_id=scenario_id,
        home_id=str(uuid.uuid4()),
        scenario_title="Утренний режим",
        actions={
            "conditions": [{"device_type": "temperature", "operator": "<", "value": 20}],
            "actions": [{"device_id": "uuid", "action": "set_temperature", "value": 22}]
        },
        is_active=True,
        created_at=datetime.now()
    )

@app.put("/scenarios/{scenario_id}",
         response_model=Scenario,
         summary="Обновление сценария",
         description="Изменение параметров сценария автоматизации",
         tags=["⚙️ Сценарии"])
async def update_scenario(
    scenario_id: str,
    scenario_update: ScenarioUpdate,
    current_user: User = Depends(get_current_user)
):
    """Обновление сценария"""
    return Scenario(
        scenario_id=scenario_id,
        home_id=str(uuid.uuid4()),
        scenario_title=scenario_update.scenario_title or "Утренний режим",
        actions=scenario_update.actions or {
            "conditions": [{"device_type": "temperature", "operator": "<", "value": 20}],
            "actions": [{"device_id": "uuid", "action": "set_temperature", "value": 22}]
        },
        is_active=scenario_update.is_active if scenario_update.is_active is not None else True,
        created_at=datetime.now()
    )

@app.delete("/scenarios/{scenario_id}",
           response_model=MessageResponse,
           summary="Удаление сценария",
           description="Удаление сценария автоматизации",
           tags=["⚙️ Сценарии"])
async def delete_scenario(
    scenario_id: str,
    current_user: User = Depends(get_current_user)
):
    """Удаление сценария"""
    return MessageResponse(message="Scenario deleted successfully")



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
