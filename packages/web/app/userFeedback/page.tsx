
import { supabase } from '../../lib/supabase/supabaseClient';
import ThreeCardLayout from '@/components/ThreeCardLayout';


export const dynamic = "force-dynamic";

export default async function userFeedback() {
  const { data: cards, error } = await supabase
    .from('cards') 
    .select("*")
    //.select("createdAt> '2023-01-11'")
    .limit(3)
    ;

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


