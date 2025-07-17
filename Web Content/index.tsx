import React from 'react';
import { Sparkles, Heart, Lightbulb } from 'lucide-react';

const SocietyOS = () => {
  return (
    <div className="max-w-4xl mx-auto p-6">
      <header className="mb-8">
        <h1 className="text-3xl font-bold flex items-center gap-2">
          <Sparkles className="w-8 h-8" />
          Welcome Home
        </h1>
        <p className="text-xl text-gray-600">Everything you need is already here</p>
      </header>

      <div className="grid grid-cols-2 gap-6">
        {/* No login needed - just direct access to resources */}
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Heart className="w-6 h-6" />
            Your Flow Today
          </h2>
          <div className="space-y-4">
            <div className="p-4 bg-blue-50 rounded-lg">
              <p>Weekly Resource Flow: $800</p>
              <p className="text-sm text-gray-600">Use it to thrive</p>
            </div>
            <div className="p-4 bg-green-50 rounded-lg">
              <p>Community Abundance Pool: $104,000</p>
              <p className="text-sm text-gray-600">For housing, business, whatever helps you grow</p>
            </div>
          </div>
        </div>

        {/* Direct connection to community */}
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Lightbulb className="w-6 h-6" />
            What Calls You?
          </h2>
          <div className="space-y-4">
            <div className="p-4 bg-purple-50 rounded-lg">
              <p>Teaching quantum physics at the park</p>
              <p className="text-sm text-gray-600">3 neighbors are curious too</p>
            </div>
            <div className="p-4 bg-yellow-50 rounded-lg">
              <p>Community garden needs plant wisdom</p>
              <p className="text-sm text-gray-600">Share what you know</p>
            </div>
          </div>
        </div>

        {/* Growth tools */}
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-bold mb-4">Expand Your Mind</h2>
          <div className="space-y-4">
            <div className="p-4 bg-indigo-50 rounded-lg">
              <p>Consciousness Exploration Guide</p>
              <p className="text-sm text-gray-600">Tools for growth, no fear or shame</p>
            </div>
            <div className="p-4 bg-pink-50 rounded-lg">
              <p>Creative Projects Brewing</p>
              <p className="text-sm text-gray-600">Art, music, ideas wanting to emerge</p>
            </div>
          </div>
        </div>

        {/* Essential work */}
        <div className="p-6 border rounded-lg">
          <h2 className="text-xl font-bold mb-4">Meaningful Work</h2>
          <div className="space-y-4">
            <div className="p-4 bg-red-50 rounded-lg">
              <p>Power Grid Optimization</p>
              <p className="text-sm text-gray-600">Fun technical challenge, helps everyone</p>
            </div>
            <div className="p-4 bg-orange-50 rounded-lg">
              <p>Local Food Production</p>
              <p className="text-sm text-gray-600">Get your hands in the earth</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SocietyOS;