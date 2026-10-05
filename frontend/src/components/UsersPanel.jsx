import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";

const EMPTY = { email: "", full_name: "" };

export default function UsersPanel() {
  const [users, setUsers] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setUsers(await api.listUsers());
    } catch (e) {
      setError(e.message);
    }
  }, []);

  useEffect(() => {
    load();
  }, [load]);

  async function create(e) {
    e.preventDefault();
    try {
      await api.createUser(form);
      setForm(EMPTY);
      setError(null);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function remove(u) {
    if (!window.confirm(`Delete ${u.email}?`)) return;
    try {
      await api.deleteUser(u.id);
      setError(null);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section>
      <form className="card form-row" onSubmit={create}>
        <h2>Add a user</h2>
        <label>
          Full name
          <input required value={form.full_name} onChange={(e) => setForm({ ...form, full_name: e.target.value })} />
        </label>
        <label className="grow">
          Email
          <input
            required
            type="email"
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </label>
        <button type="submit">Add</button>
      </form>
      {error && <div className="notice error">{error}</div>}

      <h2>Users</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Created</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {users.length === 0 && (
              <tr>
                <td colSpan={4} className="muted center">
                  No users yet.
                </td>
              </tr>
            )}
            {users.map((u) => (
              <tr key={u.id}>
                <td>{u.full_name}</td>
                <td>{u.email}</td>
                <td>{new Date(u.created_at).toLocaleDateString()}</td>
                <td>
                  <button className="danger small" onClick={() => remove(u)}>
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
