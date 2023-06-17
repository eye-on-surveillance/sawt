import React from 'react'
import RootLayout from '../app/layout'

const AboutPage = () => (
  <RootLayout>
    <section className="p-6 space-y-4">
      <h2 className="text-2xl font-bold">Points of Unity</h2>
      <p>
        Government surveillance, past and present, has been utilized to target black, brown, queer, 
        and working communities in the interest of public safety. However, the fact remains that 
        surveillance does not reduce crime and only further criminalizes those same communities. 
        Eye on Surveillance is a group of community members and organizations working together 
        under two points of unity:
      </p>
      <ul className="list-disc pl-5">
        <li>Halt the local government’s expansion of surveillance tools such as facial recognition 
        and increase oversight of current government surveillance methods.</li>
        <li>Work with communities who are targets of policing and surveillance to explore and 
        implement evidence-based community safety options that dismantle systems of oppression.</li>
      </ul>
    </section>
  </RootLayout>
)

export default AboutPage
