import { useState } from "react";
import { useAuth } from "../context/AuthContext";

export default function LoginPage() {
  const { login, register } = useAuth();
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("lead@teamboard.ru");
  const [password, setPassword] = useState("lead12345");
  const [fullName, setFullName] = useState("");
  const [role, setRole] = useState("developer");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function handleSubmit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "login") {
        await login(email, password);
      } else {
        await register(email, fullName, password, role);
      }
    } catch (err: any) {
      const detail = err?.response?.data?.detail;
      setError(typeof detail === "string" ? detail : "Не удалось выполнить вход");
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center bg-surface px-4">
      <form onSubmit={handleSubmit} className="w-full max-w-md bg-white rounded-xl shadow-sm p-8">
        <h1 className="text-2xl font-semibold mb-1">TeamBoard</h1>
        <p className="text-sm text-slate-500 mb-6">Kanban-доска студенческой команды</p>

        <div className="flex gap-2 mb-6">
          <button
            type="button"
            onClick={() => setMode("login")}
            className={`flex-1 py-2 rounded-lg text-sm font-medium ${
              mode === "login" ? "bg-accent text-white" : "bg-slate-100 text-slate-600"
            }`}
          >
            Вход
          </button>
          <button
            type="button"
            onClick={() => setMode("register")}
            className={`flex-1 py-2 rounded-lg text-sm font-medium ${
              mode === "register" ? "bg-accent text-white" : "bg-slate-100 text-slate-600"
            }`}
          >
            Регистрация
          </button>
        </div>

        {mode === "register" && (
          <>
            <label className="block text-sm text-slate-600 mb-1">Имя и фамилия</label>
            <input
              value={fullName}
              onChange={(e) => setFullName(e.target.value)}
              required
              className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-4"
            />
            <label className="block text-sm text-slate-600 mb-1">Роль в команде</label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-4"
            >
              <option value="developer">Разработчик</option>
              <option value="lead">Тимлид</option>
            </select>
          </>
        )}

        <label className="block text-sm text-slate-600 mb-1">Электронная почта</label>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-4"
        />

        <label className="block text-sm text-slate-600 mb-1">Пароль</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          minLength={6}
          className="w-full border border-slate-200 rounded-lg px-3 py-2 mb-4"
        />

        {error && <p className="text-sm text-red-600 mb-4">{error}</p>}

        <button
          type="submit"
          disabled={busy}
          className="w-full bg-accent text-white py-2.5 rounded-lg font-medium disabled:opacity-60"
        >
          {busy ? "Подождите..." : mode === "login" ? "Войти" : "Создать аккаунт"}
        </button>

        <p className="text-xs text-slate-400 mt-6 text-center">
          Демонстрационные учётные записи: lead@teamboard.ru / lead12345, dev@teamboard.ru / dev12345
        </p>
      </form>
    </div>
  );
}
