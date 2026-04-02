import React, { useState } from 'react';

const AddFruitForm = ({ addFruit }) => {
  const [fruitName, setFruitName] = useState('');
  const [fruitColor, setFruitColor] = useState('');

  const handleSubmit = (event) => {
    event.preventDefault();
    if (fruitName) {
      addFruit(fruitName, fruitColor);
      setFruitName('');
      setFruitColor('');
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        type="text"
        value={fruitName}
        onChange={(e) => setFruitName(e.target.value)}
        placeholder="Enter fruit name"
      />
      <input
        type="text"
        value={fruitColor}
        onChange={(e) => setFruitColor(e.target.value)}
        placeholder="Enter fruit color"
      />
      <button type="submit">Add Fruit</button>
    </form>
  );
};

export default AddFruitForm;