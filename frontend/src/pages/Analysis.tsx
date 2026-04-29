import { useEffect, useState } from "react";
import Table from "../components/Table";

const Analysis = () => {
  const [data, setData] = useState<any[]>([]);
  const [summary, setSummary] = useState<any>(null);
  const [filter, setFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analysis")
      .then((res) => res.json())
      .then((res) => {
        setData(res.data || []);
        setSummary(res.summary || null);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  const filtered = data.filter((item) => {
    if (filter === "ALL") return true;
    return item.status === filter;
  });

  if (loading) return <div className="p-6">Loading analysis...</div>;

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">Competitor Analysis</h1>

      {/* ✅ Summary Strip */}
      <div className="flex flex-wrap gap-4 mb-4">
        <div className="bg-gray-100 px-4 py-2 rounded">
          Total: {summary?.total_products?.toLocaleString()}
        </div>
        <div className="bg-blue-100 px-4 py-2 rounded">
          Avg: ₹{summary?.avg_price?.toFixed(2)}
        </div>
        <div className="bg-green-100 px-4 py-2 rounded">
          Min: ₹{summary?.min_price?.toFixed(2)}
        </div>
        <div className="bg-red-100 px-4 py-2 rounded">
          Max: ₹{summary?.max_price?.toFixed(2)}
        </div>
      </div>

      {/* ✅ Filters */}
      <div className="flex gap-3 mb-4">
        <button
          onClick={() => setFilter("ALL")}
          className={`px-3 py-1 rounded ${
            filter === "ALL" ? "bg-gray-400 text-white" : "bg-gray-200"
          }`}
        >
          All
        </button>

        <button
          onClick={() => setFilter("Higher")}
          className={`px-3 py-1 rounded ${
            filter === "Higher" ? "bg-red-500 text-white" : "bg-red-200"
          }`}
        >
          Overpriced
        </button>

        <button
          onClick={() => setFilter("Lower")}
          className={`px-3 py-1 rounded ${
            filter === "Lower" ? "bg-green-500 text-white" : "bg-green-200"
          }`}
        >
          Underpriced
        </button>
      </div>

      {/* ✅ Table */}
      <Table data={filtered} />
    </div>
  );
};

export default Analysis;