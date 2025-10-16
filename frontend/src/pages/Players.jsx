export default function Players() {
  return (
    <div className="space-y-6">
      <h2 className="text-3xl font-bold text-gray-800">Player Search</h2>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <input
          type="text"
          placeholder="Search for players..."
          className="w-full p-4 border border-gray-300 rounded-lg focus:ring-2 focus:ring-oracle-orange focus:border-transparent"
        />
      </div>
      
      <div className="bg-white p-6 rounded-lg shadow-md">
        <h3 className="text-xl font-semibold text-gray-800 mb-4">Player Rankings</h3>
        <div className="text-gray-500 text-center py-8">
          Search for players or view top rankings
        </div>
      </div>
    </div>
  )
}
