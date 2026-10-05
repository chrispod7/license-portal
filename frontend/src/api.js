export class ApiError extends Error {
  constructor(status, message) {
    super(message);
    this.status = status;
  }
}

function detailToMessage(detail) {
  if (typeof detail === "string") return detail;
  // FastAPI 422s carry a list of field errors.
  if (Array.isArray(detail)) return detail.map((d) => `${d.loc?.at(-1)}: ${d.msg}`).join("; ");
  return "Request failed";
}

async function request(path, { method = "GET", body } = {}) {
  const res = await fetch(`/api${path}`, {
    method,
    headers: body ? { "Content-Type": "application/json" } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (res.status === 204) return null;
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new ApiError(res.status, detailToMessage(data.detail));
  return data;
}

export const api = {
  listUsers: () => request("/users"),
  createUser: (body) => request("/users", { method: "POST", body }),
  deleteUser: (id) => request(`/users/${id}`, { method: "DELETE" }),

  listProducts: () => request("/products"),
  createProduct: (body) => request("/products", { method: "POST", body }),
  deleteProduct: (id) => request(`/products/${id}`, { method: "DELETE" }),

  listLicenses: (filters = {}) => {
    const qs = new URLSearchParams(Object.entries(filters).filter(([, v]) => v !== "" && v != null));
    return request(`/licenses${qs.size ? `?${qs}` : ""}`);
  },
  issueLicense: (body) => request("/licenses", { method: "POST", body }),
  revokeLicense: (id, reason) => request(`/licenses/${id}/revoke`, { method: "POST", body: { reason } }),
  validateLicense: (key, sku) => request("/licenses/validate", { method: "POST", body: { key, sku: sku || null } }),
};
