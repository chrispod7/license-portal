import { useState } from "react";
import { api } from "../api.js";

const REASONS = {
  malformed: "That doesn't look like a valid key (bad format or checksum).",
  not_found: "No license exists with that key.",
  wrong_product: "This key belongs to a different product.",
  revoked: "This license has been revoked.",
  expired: "This license has expired.",
};

export default function ValidatePanel() {
  const [key, setKey] = useState("");
  const [sku, setSku] = useState("");
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function submit(e) {
    e.preventDefault();
    setError(null);
    try {
      setResult(await api.validateLicense(key, sku));
    } catch (e) {
      setResult(null);
      setError(e.message);
    }
  }

  return (
    <section>
      <form className="card form-row" onSubmit={submit}>
        <h2>Validate a key</h2>
        <label className="grow">
          License key
          <input
            required
            value={key}
            onChange={(e) => setKey(e.target.value)}
            placeholder="ACME-XXXXX-XXXXX-XXXXX-XXXXX"
            spellCheck={false}
          />
        </label>
        <label>
          Product SKU (optional)
          <input value={sku} onChange={(e) => setSku(e.target.value)} placeholder="ACME" />
        </label>
        <button type="submit">Check</button>
      </form>

      {error && <div className="notice error">{error}</div>}
      {result && (
        <div className={`notice ${result.valid ? "success" : "error"}`} role="status">
          {result.valid ? (
            <>
              <strong>Valid.</strong> {result.product_sku} license
              {result.expires_at ? `, expires ${new Date(result.expires_at).toLocaleDateString()}` : ", perpetual"}.
            </>
          ) : (
            <>
              <strong>Invalid.</strong> {REASONS[result.reason] ?? result.reason}
            </>
          )}
        </div>
      )}
    </section>
  );
}
