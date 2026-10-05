import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";

export function displayStatus(lic) {
  if (lic.status === "revoked") return "revoked";
  if (lic.is_expired) return "expired";
  return "active";
}

const fmtDate = (iso) => (iso ? new Date(iso).toLocaleDateString() : "—");

export default function LicensesPanel() {
  const [licenses, setLicenses] = useState([]);
  const [users, setUsers] = useState([]);
  const [products, setProducts] = useState([]);
  const [statusFilter, setStatusFilter] = useState("");
  const [form, setForm] = useState({ user_id: "", product_id: "", expires_on: "" });
  const [error, setError] = useState(null);
  const [justIssued, setJustIssued] = useState(null);

  const load = useCallback(async () => {
    try {
      const [l, u, p] = await Promise.all([
        api.listLicenses({ status: statusFilter }),
        api.listUsers(),
        api.listProducts(),
      ]);
      setLicenses(l);
      setUsers(u);
      setProducts(p);
      setError(null);
    } catch (e) {
      setError(e.message);
    }
  }, [statusFilter]);

  useEffect(() => {
    load();
  }, [load]);

  async function issue(e) {
    e.preventDefault();
    try {
      const lic = await api.issueLicense({
        user_id: Number(form.user_id),
        product_id: Number(form.product_id),
        // A date picked in the UI means "valid through the end of that day" (UTC).
        expires_at: form.expires_on ? `${form.expires_on}T23:59:59Z` : null,
      });
      setJustIssued(lic.key);
      setForm({ user_id: "", product_id: "", expires_on: "" });
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function revoke(lic) {
    const reason = window.prompt(`Revoke ${lic.key}? Optional reason:`);
    if (reason === null) return;
    try {
      await api.revokeLicense(lic.id, reason || null);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  const canIssue = users.length > 0 && products.length > 0;

  return (
    <section>
      <form className="card form-row" onSubmit={issue}>
        <h2>Issue a license</h2>
        {!canIssue && <p className="muted">Create at least one user and one product first.</p>}
        <label>
          User
          <select required value={form.user_id} onChange={(e) => setForm({ ...form, user_id: e.target.value })}>
            <option value="">Select…</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.full_name} ({u.email})
              </option>
            ))}
          </select>
        </label>
        <label>
          Product
          <select required value={form.product_id} onChange={(e) => setForm({ ...form, product_id: e.target.value })}>
            <option value="">Select…</option>
            {products.map((p) => (
              <option key={p.id} value={p.id}>
                {p.name} ({p.sku})
              </option>
            ))}
          </select>
        </label>
        <label>
          Expires (optional)
          <input type="date" value={form.expires_on} onChange={(e) => setForm({ ...form, expires_on: e.target.value })} />
        </label>
        <button type="submit" disabled={!canIssue}>
          Issue
        </button>
      </form>

      {justIssued && (
        <div className="notice success">
          Issued <code>{justIssued}</code>
          <button className="link" onClick={() => navigator.clipboard?.writeText(justIssued)}>
            Copy
          </button>
        </div>
      )}
      {error && <div className="notice error">{error}</div>}

      <div className="toolbar">
        <h2>Licenses</h2>
        <select aria-label="Filter by status" value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
          <option value="">All statuses</option>
          <option value="active">Active</option>
          <option value="revoked">Revoked</option>
        </select>
      </div>

      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Key</th>
              <th>User</th>
              <th>Product</th>
              <th>Status</th>
              <th>Issued</th>
              <th>Expires</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {licenses.length === 0 && (
              <tr>
                <td colSpan={7} className="muted center">
                  No licenses yet.
                </td>
              </tr>
            )}
            {licenses.map((lic) => {
              const st = displayStatus(lic);
              return (
                <tr key={lic.id}>
                  <td>
                    <code>{lic.key}</code>
                  </td>
                  <td>{lic.user.full_name}</td>
                  <td>{lic.product.sku}</td>
                  <td>
                    <span className={`badge ${st}`} title={lic.revoke_reason || undefined}>
                      {st}
                    </span>
                  </td>
                  <td>{fmtDate(lic.issued_at)}</td>
                  <td>{fmtDate(lic.expires_at)}</td>
                  <td>
                    {lic.status === "active" && (
                      <button className="danger small" onClick={() => revoke(lic)}>
                        Revoke
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </section>
  );
}
