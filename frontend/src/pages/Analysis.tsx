import { useEffect, useState } from "react";
import Table from "../components/Table";

const Analysis = () => {
  const [data, setData] = useState<any[]>([]);
  const [filter, setFilter] = useState("ALL");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/analysis")
      .then((res) => res.json())
      .then((res) => {
        setData(res);
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

      <div className="flex gap-3 mb-4">
        <button onClick={() => setFilter("ALL")} className="px-3 py-1 bg-gray-200 rounded">
          All
        </button>
        <button onClick={() => setFilter("Higher")} className="px-3 py-1 bg-red-200 rounded">
          Overpriced
        </button>
        <button onClick={() => setFilter("Lower")} className="px-3 py-1 bg-green-200 rounded">
          Underpriced
        </button>
      </div>

      <Table data={filtered} />
    </div>
  );
};

export default Analysis;