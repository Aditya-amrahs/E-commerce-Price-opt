interface Props {
  data: any[];
}

const Table = ({ data }: Props) => {
  if (!data || data.length === 0) {
    return <p className="p-4">No data available</p>;
  }

  return (
    <table className="w-full border text-sm">
      <thead className="bg-gray-100">
        <tr>
          <th className="border p-2">Product</th>
          <th className="border p-2">Our Price</th>
          <th className="border p-2">Competitor</th>
          <th className="border p-2">Diff</th>
          <th className="border p-2">%</th>
          <th className="border p-2">Status</th>
          <th className="border p-2">Recommendation</th>
        </tr>
      </thead>

      <tbody>
        {data.map((item, index) => (
          <tr
            key={item.product_id || index}
            className={`text-center ${
              item.status === "Higher"
                ? "bg-red-100"
                : item.status === "Lower"
                ? "bg-green-100"
                : ""
            }`}
          >
            <td className="border p-2">
              {item.product_id?.slice(0, 8)}
            </td>
            <td className="border p-2">₹{item.ourPrice}</td>
            <td className="border p-2">₹{item.competitorPrice}</td>
            <td className="border p-2">₹{item.difference}</td>
            <td className="border p-2">{item.percentDiff}%</td>
            <td className="border p-2">{item.status}</td>
            <td className="border p-2 text-xs">
              {item.recommendation}
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
};

export default Table;