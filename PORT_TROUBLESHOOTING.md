# Port Issues Troubleshooting Guide

This guide helps you resolve common port conflicts when running the PetCare application with Docker on Windows.

## Current Configuration

The application is configured to run on:
- **API:** `http://localhost:9002`
- **PostgreSQL:** `localhost:5432` (exposed for local development)
- **MinIO:** `http://localhost:9000` (API) and `http://localhost:9001` (Console)

## Common Problem: Port Already in Use

### Symptoms
```
Error response from daemon: ports are not available: exposing port TCP 127.0.0.1:8000 -> 127.0.0.1:0: 
listen tcp4 127.0.0.1:8000: bind: An attempt was made to access a socket in a way forbidden by its access permissions.
```

### Why This Happens (Windows-Specific)

Windows reserves certain port ranges for system use, particularly ports **7681-8180**. This is managed by Windows NAT (WinNAT) and Hyper-V.

---

## Solution 1: Use Port 9002 (Current Setup) ✅

**No changes needed!** The application is already configured to use port 9002, which is outside the reserved ranges.

Update your API client (Postman, etc.) to use:
```
http://localhost:9002/auth/register
http://localhost:9002/api/...
```

---

## Solution 2: Check Which Ports Are Reserved

If you encounter port conflicts, check Windows' reserved port ranges:

### Step 1: Open PowerShell as Administrator
```powershell
# Right-click PowerShell → "Run as Administrator"
```

### Step 2: Check excluded port ranges
```powershell
netsh interface ipv4 show excludedportrange protocol=tcp
```

**Example output:**
```
Protocol tcp Port Exclusion Ranges

Start Port    End Port
----------    --------
7681          7780
7981          8080      ← Port 8000 is in this range!
8081          8180
50000         50059
```

### Step 3: Choose a port outside these ranges

**Safe port options:**
- ✅ **9002** (current - recommended)
- ✅ **8090**
- ✅ **8888**
- ✅ **3000**
- ❌ **8000** (often reserved on Windows)

---

## Solution 3: Find What's Using a Port

If a specific port (e.g., 9002) is already in use:

```powershell
# Find the process using port 9002
netstat -ano | findstr :9002
```

**Output example:**
```
TCP    127.0.0.1:9002    0.0.0.0:0    LISTENING    12345
                                                     ↑
                                                   PID (Process ID)
```

**Kill the process:**
```powershell
taskkill /PID 12345 /F
```

---

## Solution 4: Change the Port in docker-compose.yml

If you need to use a different port:

### Edit `docker-compose.yml`:
```yaml
app:
  # ... other configuration ...
  ports:
    - "127.0.0.1:YOUR_PORT:5000"  # Change YOUR_PORT to desired port
```

**Example:**
```yaml
ports:
  - "127.0.0.1:8090:5000"  # Use port 8090 instead
```

### Restart Docker:
```bash
docker compose down
docker compose up -d
```

### Update your API endpoints:
```
http://localhost:8090/auth/register
```

---

## Solution 5: Exclude a Port from Windows Reservation (Advanced)

If you absolutely need to use port 8000 and it's reserved:

### Run PowerShell as Administrator:
```powershell
# Stop Windows NAT
net stop winnat

# Reserve port 8000 for your use
netsh int ipv4 add excludedportrange protocol=tcp startport=8000 numberofports=1

# Restart Windows NAT
net start winnat
```

⚠️ **Warning:** This requires admin privileges and may affect other applications.

---

## Quick Reference

| Issue | Command | Solution |
|-------|---------|----------|
| Check reserved ports | `netsh interface ipv4 show excludedportrange protocol=tcp` | Use a port outside these ranges |
| Find process using port | `netstat -ano \| findstr :PORT` | Kill the process with `taskkill` |
| Change app port | Edit `docker-compose.yml` | Update `ports:` section |
| Port in reserved range | Use port 9002, 8090, or 8888 | Already configured for 9002 |

---

## Testing After Changes

1. **Start the application:**
   ```bash
   docker compose up -d
   ```

2. **Check container status:**
   ```bash
   docker compose ps
   ```

3. **View logs:**
   ```bash
   docker compose logs -f app
   ```

4. **Test the API:**
   ```bash
   curl http://localhost:9002/
   # or visit in browser
   ```

---

## Platform-Specific Notes

### Windows
- Port ranges 7681-8180 are often reserved
- Requires administrator privileges to modify port exclusions
- Use port 9002 (current) or 8090 to avoid conflicts

### macOS/Linux
- Typically no reserved port ranges
- Can use port 8000 without issues
- If port conflict occurs, use `lsof -i :PORT` to find the process

---

## Still Having Issues?

1. **Restart Docker Desktop completely**
2. **Check firewall settings** (Windows Defender, antivirus)
3. **Try a different port** (8090, 8888, 9002)
4. **Restart your computer** (clears temporary port reservations)

---
