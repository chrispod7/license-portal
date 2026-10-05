import { useCallback, useEffect, useState } from "react";
import { api } from "../api.js";

const EMPTY = { sku: "", name: "", description: "" };

export default function ProductsPanel() {
  const [products, setProducts] = useState([]);
  const [form, setForm] = useState(EMPTY);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      setProducts(await api.listProducts());
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
      await api.createProduct({ ...form, description: form.description || null });
      setForm(EMPTY);
      setError(null);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  async function remove(p) {
    if (!window.confirm(`Delete ${p.name}?`)) return;
    try {
      await api.deleteProduct(p.id);
      setError(null);
      load();
    } catch (e) {
      setError(e.message);
    }
  }

  return (
    <section>
      <form className="card form-row" onSubmit={create}>
        <h2>Add a product</h2>
        <label>
          SKU
          <input
            required
            pattern="[A-Za-z0-9]{2,16}"
            title="2–16 letters or digits"
            value={form.sku}
            onChange={(e) => setForm({ ...form, sku: e.target.value })}
          />
        </label>
        <label>
          Name
          <input required value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        </label>
        <label className="grow">
          Description
          <input value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        </label>
        <button type="submit">Add</button>
      </form>
      {error && <div className="notice error">{error}</div>}

      <h2>Products</h2>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>SKU</th>
              <th>Name</th>
              <th>Description</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {products.length === 0 && (
              <tr>
                <td colSpan={4} className="muted center">
                  No products yet.
                </td>
              </tr>
            )}
            {products.map((p) => (
              <tr key={p.id}>
                <td>
                  <code>{p.sku}</code>
                </td>
                <td>{p.name}</td>
                <td className="muted">{p.description}</td>
                <td>
                  <button className="danger small" onClick={() => remove(p)}>
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
