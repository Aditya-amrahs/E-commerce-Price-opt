import { useState } from "react";
import Card from "../components/Card";

const Adjust = () => {
  const [price, setPrice] = useState("");
  const [demand, setDemand] = useState("");
  const [result, setResult] = useState<any>(null);

  const handleAdjust = () => {
    if (!price || !demand) return;

    fetch(
      `http://127.0.0.1:8000/adjust?predicted_price=${price}&demand=${demand}`
    )
      .then((res) => res.json())
      .then((res) => setResult(res));
  };

  return (
    <div className="p-6">
      <Card title="Adjust Pricing (Business Logic)">

        <div className="flex gap-3 mb-3">
          <input
            type="number"
            placeholder="Predicted Price"
            className="border p-2"
            value={price}
            onChange={(e) => setPrice(e.target.value)}
          />

          <input
            type="number"
            placeholder="Demand"
            className="border p-2"
            value={demand}
            onChange={(e) => setDemand(e.target.value)}
          />
        </div>

        <button
          onClick={handleAdjust}
          className="bg-purple-500 text-white px-3 py-1"
        >
          Adjust Price
        </button>

        {result && (
          <div className="mt-4">
            <p>Base Price: ₹{result.predicted_price}</p>
            <p>Demand: {result.demand}</p>
            <p className="font-bold">
              Final Adjusted Price: ₹{result.adjusted_price}
            </p>
          </div>
        )}

      </Card>
    </div>
  );
};

export default Adjust;