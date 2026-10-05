import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, it, vi } from "vitest";
import ValidatePanel from "./ValidatePanel.jsx";

function mockFetch(body, status = 200) {
  globalThis.fetch = vi.fn().mockResolvedValue({ ok: status < 400, status, json: () => Promise.resolve(body) });
}

afterEach(() => vi.restoreAllMocks());

describe("ValidatePanel", () => {
  it("shows a success message for a valid key", async () => {
    mockFetch({ valid: true, product_sku: "ACME", expires_at: null });
    render(<ValidatePanel />);

    await userEvent.type(screen.getByLabelText(/license key/i), "ACME-AAAAA-BBBBB-CCCCC-DDDDD");
    await userEvent.click(screen.getByRole("button", { name: /check/i }));

    expect(await screen.findByRole("status")).toHaveTextContent(/valid.*ACME license, perpetual/i);
    const [url, init] = fetch.mock.calls[0];
    expect(url).toBe("/api/licenses/validate");
    expect(JSON.parse(init.body)).toEqual({ key: "ACME-AAAAA-BBBBB-CCCCC-DDDDD", sku: null });
  });

  it("explains why a key is invalid", async () => {
    mockFetch({ valid: false, reason: "revoked" });
    render(<ValidatePanel />);

    await userEvent.type(screen.getByLabelText(/license key/i), "whatever");
    await userEvent.click(screen.getByRole("button", { name: /check/i }));

    expect(await screen.findByRole("status")).toHaveTextContent(/has been revoked/i);
  });
});
