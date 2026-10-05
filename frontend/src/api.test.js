import { afterEach, describe, expect, it, vi } from "vitest";
import { ApiError, api } from "./api.js";
import { displayStatus } from "./components/LicensesPanel.jsx";

afterEach(() => vi.restoreAllMocks());

describe("api", () => {
  it("builds license filter query strings and skips empty values", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({ ok: true, status: 200, json: () => Promise.resolve([]) });
    await api.listLicenses({ status: "revoked", user_id: "" });
    expect(fetch.mock.calls[0][0]).toBe("/api/licenses?status=revoked");
  });

  it("turns FastAPI error details into ApiError", async () => {
    globalThis.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 409,
      json: () => Promise.resolve({ detail: "A product with that SKU already exists" }),
    });
    await expect(api.createProduct({ sku: "X" })).rejects.toEqual(
      expect.objectContaining({ status: 409, message: "A product with that SKU already exists" }),
    );
    await expect(api.createProduct({ sku: "X" })).rejects.toBeInstanceOf(ApiError);
  });
});

describe("displayStatus", () => {
  it("prefers revoked over expired", () => {
    expect(displayStatus({ status: "revoked", is_expired: true })).toBe("revoked");
    expect(displayStatus({ status: "active", is_expired: true })).toBe("expired");
    expect(displayStatus({ status: "active", is_expired: false })).toBe("active");
  });
});
