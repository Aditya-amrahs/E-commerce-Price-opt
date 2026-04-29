import { useState } from "react";
import Card from "../components/Card";

const Predict = () => {
  const [index, setIndex] = useState("");
  const [result, setResult] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = () => {
    if (!index) return;

    setLoading(true);

    fetch(`http://127.0.0.1:8000/price?index=${index}`)
      .then((res) => res.json())
      .then((res) => {
        setResult(res);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  };

  return (
    <div className="p-6">
      <Card title="Predict Price (ML Model)">

        {/* Input */}
        <input
          type="number"
          placeholder="Enter row index (e.g. 0, 10, 50)"
          className="border p-2 mr-2"
          value={index}
          onChange={(e) => setIndex(e.target.value)}
        />

        {/* Button */}
        <button
          onClick={handleSubmit}
          className="bg-blue-500 text-white px-3 py-1"
        >
          Predict
        </button>

        {/* Loading */}
        {loading && <p className="mt-3">Predicting...</p>}

        {/* Result */}
        {result && (
          <div className="mt-4 space-y-2">
            <p>💰 Base Price: ₹{result.base_price.toFixed(2)}</p>
            <p>📈 Final Price: ₹{result.final_price.toFixed(2)}</p>
            <p className="text-sm text-gray-500">{result.message}</p>
          </div>
        )}

      </Card>
    </div>
  );
};

export default Predict;