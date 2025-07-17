import React from 'react';
import { Star, Brain, Heart, Sparkles } from 'lucide-react';

const PersonalImpact = () => {
  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      <h2 className="text-3xl font-bold text-center">Your Life Changes</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {/* Today */}
        <div className="p-4 border rounded-lg">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Star className="w-5 h-5" />
            Monday Morning
          </h3>
          <div className="space-y-2 text-gray-600">
            <p>Wake up when rested</p>
            <p>No forced commute</p>
            <p>Choose your purpose</p>
            <p>Create something real</p>
          </div>
        </div>

        {/* Learning */}
        <div className="p-4 border rounded-lg">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Brain className="w-5 h-5" />
            Learn Anything
          </h3>
          <div className="space-y-2 text-gray-600">
            <p>Follow curiosity</p>
            <p>No artificial limits</p>
            <p>Share knowledge</p>
            <p>Grow together</p>
          </div>
        </div>

        {/* Community */}
        <div className="p-4 border rounded-lg">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Heart className="w-5 h-5" />
            Real Connection
          </h3>
          <div className="space-y-2 text-gray-600">
            <p>Help neighbors</p>
            <p>Build community</p>
            <p>Share resources</p>
            <p>Care for each other</p>
          </div>
        </div>

        {/* Future */}
        <div className="p-4 border rounded-lg">
          <h3 className="font-bold mb-4 flex items-center gap-2">
            <Sparkles className="w-5 h-5" />
            Better World
          </h3>
          <div className="space-y-2 text-gray-600">
            <p>Clean energy</p>
            <p>Local food</p>
            <p>No waste</p>
            <p>Real progress</p>
          </div>
        </div>
      </div>

      {/* Stories */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
        <div className="p-6 border rounded-lg bg-gradient-to-br from-green-50 to-blue-50">
          <h3 className="font-bold mb-4">Sarah's Story</h3>
          <p className="text-gray-600">
            "I always wanted to teach quantum physics. Now I do it in the park on Thursdays. 
            Kids understand it better than my old university students because they're learning 
            from curiosity, not for grades."
          </p>
        </div>

        <div className="p-6 border rounded-lg bg-gradient-to-br from-purple-50 to-pink-50">
          <h3 className="font-bold mb-4">Mike's Story</h3>
          <p className="text-gray-600">
            "Used to fix washing machines. Now I teach people how to build ones that last forever. 
            We saved enough metal last month to power 1,000 homes for a year."
          </p>
        </div>
      </div>
    </div>
  );
};

export default PersonalImpact;