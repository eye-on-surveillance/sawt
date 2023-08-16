export const randItem = (items: any) => {
  return items[Math.floor(Math.random() * items.length)];
};
