import client from "./client";

/**
 * POST /predict (Bearer required)
 * multipart/form-data, field name MUST be "image" per
 * Body_predict_image_predict_post in openapi.json.
 *
 * The response schema is an open object (additionalProperties: string|number) —
 * the backend does not guarantee a fixed set of keys, so callers must not
 * assume specific fields exist.
 */
export async function predictImage(file) {
  const formData = new FormData();
  formData.append("image", file);
  const { data } = await client.post("/predict", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

/**
 * GET /history?page=&page_size= (Bearer required)
 * -> PredictionHistoryResponse { items, page, page_size, total }
 */
export async function getHistory({ page = 1, pageSize = 20 } = {}) {
  const { data } = await client.get("/history", {
    params: { page, page_size: pageSize },
  });
  return data;
}
