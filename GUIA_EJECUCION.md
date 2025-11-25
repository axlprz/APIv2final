# Guía de Ejecución y Pruebas - Sistema Distribuido 2PC

## Estado Actual

**Sistema funcionando localmente sin Docker**
- Servicios adaptados para usar SQLite en lugar de MySQL
- 3 servicios ejecutándose: Bank A (8001), Bank B (8002), API Final (9000)
- Pruebas verificadas y funcionando

## ADVERTENCIA IMPORTANTE: Estado de Bases de Datos

**Las transferencias exitosas modifican permanentemente los balances en SQLite.**

Si ejecutaste pruebas exitosas previamente, los balances actuales serán diferentes a los iniciales. Esto causará que las pruebas 3.2-3.4 fallen (retornarán COMMITTED en lugar de ABORTED).

**Solución Rápida**:
```powershell
# Detener servicios y resetear bases de datos
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid"
python reset_databases.py
# Luego reiniciar servicios (ver sección "Inicio de Servicios")
```

Ver sección "Verificar Balances Antes de Pruebas" para detalles completos.

## Requisitos Previos

1. **Python 3.8+** instalado y en PATH
2. **Dependencias instaladas**:
   ```powershell
   pip install fastapi uvicorn requests sqlmodel passlib[bcrypt] PyJWT python-dotenv
   ```
3. **bcrypt versión compatible** (4.0.1):
   ```powershell
   pip uninstall -y bcrypt
   pip install bcrypt==4.0.1
   ```

## Inicio de Servicios

### Método 1: Script Automático (Más Fácil)

Ejecuta el script de PowerShell que inicia todo y verifica automáticamente:

```powershell
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal"
.\start_services.ps1
```

El script:
- ✓ Detecta servicios corriendo y pregunta si reiniciar
- ✓ Inicia Bank A, Bank B y API Final
- ✓ Verifica que todos respondan correctamente
- ✓ Muestra logs en ventanas separadas
- ✓ Reporta estado final

### Método 2: Comandos Manuales (Control Total)

Este comando inicia todos los servicios y verifica que estén funcionando:

```powershell
# Copiar y pegar este bloque completo
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
Start-Process python -ArgumentList "-m","uvicorn","app_local:app","--host","127.0.0.1","--port","8001" -WindowStyle Normal
Write-Host "Bank A iniciado en puerto 8001" -ForegroundColor Green

cd "..\bank_b"
Start-Process python -ArgumentList "-m","uvicorn","app_local:app","--host","127.0.0.1","--port","8002" -WindowStyle Normal
Write-Host "Bank B iniciado en puerto 8002" -ForegroundColor Green

cd "..\..\API final"
$env:ENV_MODE="local"
Start-Process python -ArgumentList "-m","uvicorn","app:app","--host","127.0.0.1","--port","9000" -WindowStyle Normal
Write-Host "API Final iniciada en puerto 9000" -ForegroundColor Green

# Esperar y verificar
Start-Sleep -Seconds 4
Write-Host "`n=== Verificando servicios ===" -ForegroundColor Cyan
try { 
    $a = Invoke-RestMethod -Uri "http://localhost:8001/health"
    Write-Host "✓ Bank A (8001): $($a.status)" -ForegroundColor Green
} catch { Write-Host "✗ Bank A (8001): No responde" -ForegroundColor Red }

try { 
    $b = Invoke-RestMethod -Uri "http://localhost:8002/health"
    Write-Host "✓ Bank B (8002): $($b.status)" -ForegroundColor Green
} catch { Write-Host "✗ Bank B (8002): No responde" -ForegroundColor Red }

try { 
    $c = Invoke-RestMethod -Uri "http://localhost:9000/health"
    Write-Host "✓ API Final (9000): $($c.status)" -ForegroundColor Green
} catch { Write-Host "✗ API Final (9000): No responde" -ForegroundColor Red }

Write-Host "`n Todos los servicios iniciados. Puedes comenzar las pruebas." -ForegroundColor Green
```

### Opción Alternativa: Ventanas Ocultas (Sin Logs Visibles)

```powershell
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
Start-Process python -ArgumentList "-m","uvicorn","app_local:app","--host","127.0.0.1","--port","8001" -WindowStyle Hidden

cd "..\bank_b"
Start-Process python -ArgumentList "-m","uvicorn","app_local:app","--host","127.0.0.1","--port","8002" -WindowStyle Hidden

cd "..\..\API final"
$env:ENV_MODE="local"
Start-Process python -ArgumentList "-m","uvicorn","app:app","--host","127.0.0.1","--port","9000" -WindowStyle Hidden

Start-Sleep -Seconds 4
Write-Host "Servicios iniciados en background" -ForegroundColor Green
```

### Verificación Manual de Servicios

```powershell
# Verificar uno por uno
Invoke-RestMethod -Uri "http://localhost:8001/health"  # Bank A
Invoke-RestMethod -Uri "http://localhost:8002/health"  # Bank B
Invoke-RestMethod -Uri "http://localhost:9000/health"  # API Final

# O verificar todos a la vez
Write-Host "Bank A:"; Invoke-RestMethod -Uri "http://localhost:8001/health"
Write-Host "Bank B:"; Invoke-RestMethod -Uri "http://localhost:8002/health"
Write-Host "API Final:"; Invoke-RestMethod -Uri "http://localhost:9000/health"
```

## Troubleshooting: Error "Unable to connect to the remote server"

### Síntoma
```
Invoke-RestMethod : Unable to connect to the remote server
```

### Causa
Los servicios no están corriendo. Esto puede ocurrir si:
1. No iniciaste los servicios después de reiniciar la computadora
2. Los servicios se cerraron por error
3. Cerraste las ventanas de terminal de los servicios

### Solución

#### Paso 1: Verificar si hay servicios corriendo
```powershell
Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, ProcessName
```

Si no aparece nada, significa que **no hay servicios corriendo**.

#### Paso 2: Iniciar servicios
Ejecuta el script completo de inicio de la sección anterior.

#### Paso 3: Verificar que respondan
```powershell
try {
    Invoke-RestMethod -Uri "http://localhost:9000/health"
    Write-Host "API Final funcionando correctamente" -ForegroundColor Green
} catch {
    Write-Host "API Final NO responde. Verifica los logs en la ventana del servicio." -ForegroundColor Red
}
```

#### Paso 4: Si continúa el error
```powershell
# Matar todos los procesos Python y reiniciar
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Ejecutar script de inicio nuevamente
# (ver sección "Script Completo de Inicio")
```

### Tip: Verificar Puertos en Uso
```powershell
# Ver qué está usando los puertos 8001, 8002, 9000
netstat -ano | findstr ":8001"
netstat -ano | findstr ":8002"
netstat -ano | findstr ":9000"
```

## Pruebas de los Resultados 3.1 a 3.7

### IMPORTANTE: Verificar Balances Antes de Pruebas

**Las transferencias exitosas modifican los balances permanentemente**. Si ya ejecutaste pruebas exitosas, los balances actuales serán diferentes a los iniciales, lo que causará que las pruebas 3.2-3.4 **no funcionen como se espera**.

#### Verificar Balances Actuales
```powershell
# Bank A
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
python -c "import sqlite3; conn = sqlite3.connect('bank_a.db'); print('Bank A:'); [print(f'  Cuenta {r[0]}: {r[1]}') for r in conn.execute('SELECT * FROM accounts').fetchall()]"

# Bank B
cd "..\bank_b"
python -c "import sqlite3; conn = sqlite3.connect('bank_b.db'); print('Bank B:'); [print(f'  Cuenta {r[0]}: {r[1]}') for r in conn.execute('SELECT * FROM accounts').fetchall()]"
```

#### Resetear a Balances Iniciales
```powershell
# Detener servicios primero
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Resetear bases de datos
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid"
python reset_databases.py

# Reiniciar servicios (ver sección "Inicio de Servicios")
```

**Balances Iniciales Esperados**:
- Bank A - Cuenta 1: **1000.0**
- Bank A - Cuenta 2: **500.0**
- Bank B - Cuenta 1: **200.0**
- Bank B - Cuenta 2: **800.0**

---

## CHECKPOINT: Verificar Servicios Antes de Pruebas

** IMPORTANTE**: Antes de ejecutar cualquier prueba, DEBES verificar que los servicios estén corriendo.

### Paso 1: Verificar que los Servicios Estén Activos

```powershell
# Verificar servicios (EJECUTA ESTO PRIMERO)
Write-Host "`n Verificando servicios..." -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod -Uri "http://localhost:9000/health" -TimeoutSec 2
    Write-Host "API Final respondiendo correctamente ($($health.participants_configured) participantes)" -ForegroundColor Green
} catch {
    Write-Host "ERROR: API Final NO está corriendo" -ForegroundColor Red
    Write-Host "SOLUCIÓN: Ejecuta primero el script de inicio:" -ForegroundColor Yellow
    Write-Host "  .\start_services.ps1" -ForegroundColor White
    Write-Host "O sigue la sección 'Inicio de Servicios' de esta guía.`n" -ForegroundColor Yellow
    exit
}

try {
    Invoke-RestMethod -Uri "http://localhost:8001/health" -TimeoutSec 2 | Out-Null
    Invoke-RestMethod -Uri "http://localhost:8002/health" -TimeoutSec 2 | Out-Null
    Write-Host "Bank A y Bank B respondiendo correctamente" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Uno o más servicios bancarios NO están corriendo" -ForegroundColor Red
    Write-Host "SOLUCIÓN: Ejecuta el script de inicio completo.`n" -ForegroundColor Yellow
    exit
}

Write-Host "`n Todos los servicios están corriendo. Puedes continuar con las pruebas.`n" -ForegroundColor Green
```

### Paso 2: Obtener Token JWT

**Solo ejecuta esto si el paso anterior fue exitoso:**

```powershell
$body = @{username="admin"; password="admin"} | ConvertTo-Json
$response = Invoke-RestMethod -Uri "http://localhost:9000/auth/login" -Method Post -Body $body -ContentType "application/json"
$token = $response.access_token
$headers = @{Authorization="Bearer $token"}
Write-Host "Token JWT obtenido exitosamente" -ForegroundColor Green
```

**Si obtienes error aquí**, significa que los servicios NO están corriendo. Ve a la sección "Troubleshooting: Error 'Unable to connect to the remote server'" más abajo.

### 3.1 - Prueba de Flujo Exitoso VERIFICADO

**Descripción**: Transferir 50 de cuenta 1 a cuenta 2

```powershell
$transferBody = @{amount=50; from_account=1; to_account=2} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:9000/transfer" -Method Post -Headers $headers -Body $transferBody -ContentType "application/json"
$result | ConvertTo-Json -Depth 5
```

**Resultado Esperado**:
- `status: "COMMITTED"`
- Ambos participantes con `prepare_status: "READY"` y `commit_status: "COMMITTED"`

**Resultado Real**: ÉXITO
```json
{
  "tx_id": "4639a972-4321-432c-afb9-1112622675aa",
  "status": "COMMITTED",
  "participants": [
    {
      "name": "bank_a",
      "role": "debit",
      "prepare_status": "READY",
      "commit_status": "COMMITTED"
    },
    {
      "name": "bank_b",
      "role": "credit",
      "prepare_status": "READY",
      "commit_status": "COMMITTED"
    }
  ]
}
```

### 3.2 - Prueba de Falla en PREPARE (Saldo Insuficiente)

**Descripción**: Intentar transferir más de lo disponible

**Prerequisito**: Verificar que cuenta 1 de Bank A tenga balance inicial (1000.0). Si ya ejecutaste transferencias exitosas, el balance será menor y esta prueba podría fallar.

```powershell
# Verificar balance actual primero
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
python -c "import sqlite3; conn = sqlite3.connect('bank_a.db'); row = conn.execute('SELECT balance FROM accounts WHERE id=1').fetchone(); print(f'Balance actual cuenta 1: {row[0]}'); print(f'Para ABORT, usar amount > {row[0]}')"

# Ejecutar transferencia con monto mayor al balance
$transferBody = @{amount=5000; from_account=1; to_account=2} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:9000/transfer" -Method Post -Headers $headers -Body $transferBody -ContentType "application/json"
Write-Host "STATUS: $($result.status)" -ForegroundColor $(if($result.status -eq 'ABORTED'){'Green'}else{'Red'})
$result.participants | ForEach-Object { Write-Host "  $($_.name): PREPARE=$($_.prepare_status)" }
```

**Resultado Esperado**:
- `status: "ABORTED"`
- Bank A con `prepare_status: "ABORT"`
- Bank B con `prepare_status: "READY"` (no se ejecutó COMMIT en ninguno)

### 3.3 - Prueba de Falla en COMMIT

**Descripción**: Simular caída de Bank B después de PREPARE pero antes/durante COMMIT

**Nota**: Esta prueba requiere timing preciso. El servicio debe caer **después** de responder READY en PREPARE pero **antes** de recibir COMMIT.

```powershell
# Opción 1: Detener Bank B ANTES de la transferencia
# Esto causará fallo en PREPARE (no en COMMIT)
Get-Process python | Where-Object {$_.CommandLine -like "*8002*"} | Stop-Process -Force
Start-Sleep -Seconds 1

# Intentar transferencia
$transferBody = @{amount=20; from_account=1; to_account=2} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:9000/transfer" -Method Post -Headers $headers -Body $transferBody -ContentType "application/json"
Write-Host "STATUS: $($result.status)" -ForegroundColor $(if($result.status -eq 'ABORTED'){'Green'}else{'Red'})
$result.participants | ForEach-Object { 
    Write-Host "  $($_.name): PREPARE=$($_.prepare_status), COMMIT=$($_.commit_status)"
    if ($_.error) { Write-Host "    Error: $($_.error)" -ForegroundColor Yellow }
}

# Reiniciar Bank B para siguientes pruebas
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_b"
Start-Process python -ArgumentList "-m","uvicorn","app_local:app","--host","127.0.0.1","--port","8002" -WindowStyle Hidden
Start-Sleep -Seconds 3
```

**Resultado Esperado** (Servicio caído antes de PREPARE):
- `status: "ABORTED"`
- Bank A: `prepare_status: "READY"`, `commit_status: null`
- Bank B: `prepare_status: "UNREACHABLE"`, error de conexión

**Comportamiento Real del Sistema**:
- Si Bank B cae **antes** de PREPARE → fallo detectado en fase PREPARE
- Si Bank B cae **durante** COMMIT → Bank A podría commitear, Bank B fallaría (inconsistencia temporal)
- Rollback se invoca pero sin tabla `prepared_tx` no revierte cambios reales

### 3.4 - Servicio No Disponible Antes de PREPARE

**Descripción**: Detener Bank A antes de la transferencia para simular servicio completamente inaccesible

```powershell
# Detener Bank A
Get-Process python | Where-Object {$_.CommandLine -like "*8001*"} | Stop-Process -Force
Start-Sleep -Seconds 1

# Intentar transferencia
$transferBody = @{amount=30; from_account=1; to_account=2} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:9000/transfer" -Method Post -Headers $headers -Body $transferBody -ContentType "application/json"
Write-Host "STATUS: $($result.status)" -ForegroundColor $(if($result.status -eq 'ABORTED'){'Green'}else{'Red'})
$result.participants | ForEach-Object { 
    Write-Host "  $($_.name): PREPARE=$($_.prepare_status)"
    if ($_.error) { Write-Host "    Error: $($_.error.Substring(0, [Math]::Min(80, $_.error.Length)))..." -ForegroundColor Yellow }
}

# Reiniciar Bank A para siguientes pruebas
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
Start-Process python -ArgumentList "-m","uvicorn","app_local:app","--host","127.0.0.1","--port","8001" -WindowStyle Hidden
Start-Sleep -Seconds 3
```

**Resultado Esperado**:
- `status: "ABORTED"`
- Bank A con `prepare_status: "UNREACHABLE"`
- Bank A con mensaje de error indicando conexión rechazada/timeout
- Bank B con `prepare_status: "READY"` (alcanzado exitosamente pero no se ejecutó COMMIT)

**Verificación de Reintentos**:
El coordinador intenta `max_retries + 1` veces (default: 3 intentos) antes de marcar UNREACHABLE.

### 3.5 - Consistencia tras Abortos

**Descripción**: Verificar que balances no cambian tras abortos

```powershell
# Consultar transacciones para confirmar abortos
$txList = Invoke-RestMethod -Uri "http://localhost:9000/transactions" -Method Get -Headers $headers
$txList | Where-Object {$_.status -eq 'ABORTED'} | Measure-Object

# Verificar balance en Bank A directamente (requiere acceso a SQLite)
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
python -c "import sqlite3; conn = sqlite3.connect('bank_a.db'); print(conn.execute('SELECT * FROM accounts').fetchall())"
```

**Resultado Esperado**:
- Balances permanecen sin cambios en transacciones abortadas

### 3.6 - Reconciliación de Transacciones Estancadas

**Descripción**: Marcar transacciones PREPARED antiguas como ABORTED

```powershell
# Insertar transacción PREPARED simulada (requiere acceso directo a DB)
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\API final"
python -c @"
import sqlite3
from datetime import datetime, timedelta
conn = sqlite3.connect('transactions.db')
old_time = (datetime.utcnow() - timedelta(minutes=10)).isoformat()
conn.execute('INSERT INTO transactionlog (tx_id, status, participants, created_at, updated_at) VALUES (?, ?, ?, ?, ?)',
             ('test-stuck-tx', 'PREPARED', '[]', old_time, old_time))
conn.commit()
conn.close()
print('Transacción PREPARED simulada insertada')
"@

# Ejecutar reconciliación
$reconResult = Invoke-RestMethod -Uri "http://localhost:9000/admin/reconcile" -Method Post -Headers $headers
$reconResult | ConvertTo-Json
```

**Resultado Esperado**:
- Retorna lista de transacciones marcadas como ABORTED
- La transacción `test-stuck-tx` debe aparecer en la lista

### 3.7 - Extensión con Tercer Participante

**Descripción**: Agregar Bank C como participante mirror

**Preparación**:
1. Copiar `participants_3nodes.json` a `participants.json` o crear Bank C real
2. Reiniciar API Final con nuevo config

```powershell
# Opción 1: Crear Bank C (copia de Bank B)
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid"
Copy-Item -Recurse bank_b bank_c
cd bank_c
# Editar app_local.py para usar bank_c.db en lugar de bank_b.db

# Iniciar Bank C
Start-Process python -ArgumentList "-m","uvicorn","app_local:app","--host","127.0.0.1","--port","8003" -WindowStyle Hidden

# Opción 2: Usar variable de entorno
$env:BANK_PARTICIPANTS="bank_a|http://localhost:8001|debit,bank_b|http://localhost:8002|credit,bank_c|http://localhost:8003|mirror"

# Reiniciar API Final
Get-Process python | Where-Object {$_.CommandLine -like "*9000*"} | Stop-Process -Force
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\API final"
Start-Process python -ArgumentList "-m","uvicorn","app:app","--host","127.0.0.1","--port","9000" -WindowStyle Hidden

# Transferencia con 3 participantes
Start-Sleep -Seconds 3
$transferBody = @{amount=25; from_account=1; to_account=2} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:9000/transfer" -Method Post -Headers $headers -Body $transferBody -ContentType "application/json"
$result.participants.Count  # Debe ser 3
```

**Resultado Esperado**:
- 3 participantes en la respuesta
- Todos con estado COMMITTED si Bank C está disponible

## Detener Servicios

```powershell
# Detener todos los procesos Python
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force
```

## Archivos Importantes

- **`API final/app.py`**: Coordinador avanzado con JWT y reconciliación
- **`acid/bank_a/app_local.py`**: Servicio débito con SQLite
- **`acid/bank_b/app_local.py`**: Servicio crédito con SQLite
- **`API final/config.py`**: Configuración centralizada
- **`API final/participants.json`**: Lista de participantes (2 nodos por defecto)
- **`API final/participants_3nodes.json`**: Lista con 3 participantes para prueba 3.7

## Problemas Conocidos y Soluciones

### 1. Docker no disponible
**Resuelto**: Servicios adaptados para ejecutarse sin Docker usando SQLite

### 2. Error bcrypt `__about__`
**Resuelto**: Downgrade a bcrypt 4.0.1
```powershell
pip uninstall -y bcrypt
pip install bcrypt==4.0.1
```

### 3. Scripts .ps1 no se pueden ejecutar
**Solución**: Cambiar política temporalmente
```powershell
Set-ExecutionPolicy -ExecutionPolicy Bypass -Scope Process -Force
```

### 4. API Final carga tercer participante no disponible
**Resuelto**: `participants.json` actualizado a 2 nodos por defecto

### 5. Pruebas 3.2, 3.3, 3.4 retornan COMMITTED en lugar de ABORTED

**Causa**: Los balances de las cuentas han cambiado debido a transferencias exitosas previas.

**Explicación**: 
- Cada transferencia exitosa (COMMITTED) **modifica permanentemente** los balances en SQLite
- Si ejecutaste la prueba 3.1 (transferir 50 de cuenta 1 a 2), el balance de cuenta 1 en Bank A ahora es **950.0** en lugar de 1000.0
- Cuando intentas la prueba 3.2 con `amount=5000`, si el balance es mayor a 5000, la validación pasa y retorna COMMITTED

**Diagnóstico**:
```powershell
# Verificar balances actuales
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
python -c "import sqlite3; conn = sqlite3.connect('bank_a.db'); print('Balances Bank A:'); [print(f'  Cuenta {r[0]}: {r[1]}') for r in conn.execute('SELECT * FROM accounts').fetchall()]"
```

**Solución 1 - Resetear Bases de Datos** (Recomendado):
```powershell
# Detener servicios
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force

# Ejecutar script de reset
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid"
python reset_databases.py

# Reiniciar servicios (ver sección "Inicio de Servicios")
```

**Solución 2 - Usar Montos Dinámicos**:
```powershell
# Consultar balance actual
cd "c:\Users\axelp\OneDrive\Desktop\UAQ\sist distribui2\ProyectoFinal\acid\bank_a"
$balance = python -c "import sqlite3; conn = sqlite3.connect('bank_a.db'); print(conn.execute('SELECT balance FROM accounts WHERE id=1').fetchone()[0])"

# Usar monto mayor al balance para forzar ABORT
$amountToFail = [math]::Ceiling([double]$balance) + 100
Write-Host "Balance actual: $balance, usando amount: $amountToFail para forzar ABORT"

# Ejecutar transferencia
$transferBody = @{amount=$amountToFail; from_account=1; to_account=2} | ConvertTo-Json
$result = Invoke-RestMethod -Uri "http://localhost:9000/transfer" -Method Post -Headers $headers -Body $transferBody -ContentType "application/json"
$result.status  # Ahora debe ser ABORTED
```

**Prevención**: Siempre resetear bases de datos antes de iniciar una sesión completa de pruebas.

## Base de Datos

Cada servicio crea su propia base de datos SQLite con datos de prueba:

- **Bank A** (`bank_a.db`):
  - Cuenta 1: Balance inicial 1000.0
  - Cuenta 2: Balance inicial 500.0

- **Bank B** (`bank_b.db`):
  - Cuenta 1: Balance inicial 200.0
  - Cuenta 2: Balance inicial 800.0

- **API Final** (`transactions.db`):
  - Usuario admin: username=`admin`, password=`admin`, role=`admin`
  - Tabla `TransactionLog`: Registro de todas las transacciones 2PC

## Próximos Pasos Recomendados

1. Implementar endpoint `/balance` real en bancos
2. Crear Bank C para completar prueba 3.7
3. Agregar persistencia de estado PREPARED en tabla `prepared_tx`
4. Implementar logs de auditoría para cumplimiento