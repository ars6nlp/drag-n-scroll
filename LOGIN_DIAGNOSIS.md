# 🔴 КРИТИЧЕСКАЯ ПРОБЛЕМА: Users disappear after 20 minutes

## Root Cause Analysis

### ❌ Проблема найдена: SQLite на Render НЕ ПЕРСИСТЕНТЕН!

**Что происходит:**
1. User регистрируется → данные сохраняются в SQLite (db.sqlite3)
2. Через ~20 минут Render перезапускает контейнер
3. **ВСЕ ДАННЫЕ ТЕРЯЮТСЯ** - SQLite файл стирается
4. User исчезает из базы → логин не работает

**Почему так происходит:**
- На Render бесплатные контейнеры перезапускаются каждые ~15-20 минут
- SQLite файлы НЕ сохраняются между перезапусками
- Нужен PostgreSQL (база данных в облаке) для персистентности

---

## 🛠️ РЕШЕНИЕ: Настроить PostgreSQL на Render

### Step 1: Создать PostgreSQL базу данных на Render

1. Откройте [Render Dashboard](https://dashboard.render.com/)
2. Перейдите в ваш backend сервис
3. Нажмите **"Add Database"** или создайте новую PostgreSQL базу
4. Дождитесь создания базы данных

### Step 2: Скопировать DATABASE_URL

1. В созданной PostgreSQL базе, найдите **"Internal Database URL"**
2. Скопируйте URL (выглядит как: `postgresql://user:password@host/database`)

### Step 3: Добавить DATABASE_URL в Backend Service

1. Откройте ваш Backend Service на Render
2. Перейдите в раздел **"Environment"**
3. Добавьте новую переменную окружения:
   - Key: `DATABASE_URL`
   - Value: (вставьте скопированный URL из Step 2)
4. Нажмите **"Save Changes"**
5. Сервис автоматически перезапустится с новой базой данных

### Step 4: Запустить миграции

После настройки DATABASE_URL:

1. Откройте в браузере: `https://drag-n-scroll.onrender.com/api/migrate/`
2. Должно появиться: `{"status": "success", "message": "Migrations completed successfully"}`

### Step 5: Проверить что база данных переключилась

Откройте в браузере: `https://drag-n-scroll.onrender.com/api/debug/database/`

Должно показать:
```json
{
  "database_type": "PostgreSQL",
  "is_persistent": true,
  "persistence": "GOOD - Data persists across restarts"
}
```

Если показывает `"database_type": "SQLite"` и `"is_persistent": false` - значит DATABASE_URL не настроен правильно!

---

## ✅ Как проверить что всё работает:

1. **Зарегистрируйте нового юзера**
2. **Проверьте что логин работает**
3. **Подождите 20-30 минут** (или перезапустите сервис на Render)
4. **Попробуйте залогиниться снова**
5. **Если логин работает** → база данных персистентная! ✅

---

## 📊 Статус диагностики

### ✅ Backend (Render) - РАБОТАЕТ ИДЕАЛЬНО!
- ✅ Регистрация: Status 201
- ✅ Логин: Status 200
- ✅ Токены выдаются правильно
- ✅ `/user/me/` работает
- ✅ Профиль создается автоматически
- ✅ Прогресс создается автоматически

### ✅ Frontend-Backend Connection - РАБОТАЕТ!
- ✅ CORS настроен правильно
- ✅ API calls работают
- ✅ Токены сохраняются

### ❌ БАЗА ДАННЫХ: КРИТИЧЕСКАЯ ПРОБЛЕМА
- ❌ Используется SQLite (НЕ ПЕРСИСТЕНТНЫЙ)
- ✅ Добавлено обнаружение типа базы: `/api/debug/database/`
- ⏳ Ожидает настройки DATABASE_URL на Render

---

## 🚨 Если проблема сохраняется после настройки DATABASE_URL:

### 1. ЖЕСТКАЯ ПЕРЕЗАГРУЗКА:
- Windows: `Ctrl + Shift + R`
- Mac: `Cmd + Shift + R`

### 2. ОЧИСТИТЬ LOCALSTORAGE:
Откройте DevTools → Console → введите:
```javascript
localStorage.clear()
location.reload()
```

### 3. Проверить консоль браузера:
- Откройте DevTools (F12)
- Перейдите в Console
- Попробуйте залогиниться
- Ищите ошибки красного цвета

### 4. Инкогнито режим:
Если всё ещё не работает - попробуйте в инкогнито режиме
