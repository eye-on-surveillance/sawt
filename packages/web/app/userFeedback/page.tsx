
import { supabase } from '../../lib/supabase/supabaseClient';
import ThreeCardLayout from '../../components/ThreeCardLayout';
import NewComment from '@/components/Comment';

export const dynamic = "force-dynamic";

export default async function userFeedback() {
  const { data: cards, error } = await supabase
    .from('cards') 
    .select('*')
    .limit(3);
  console.log("helloworld");

  if (error) {
    console.error("Error fetching cards:", error);
    // Handle the error appropriately in your UI  
  }



  return (
    <>
      <ThreeCardLayout cards = {cards}/>
    </>
  );
};


