/* The only place to set the public contact address. Leave empty until it exists. */
const CONTACT_EMAIL = "listakauffmann@gmail.com";

const COPY = {
  de: {
    title: "Kauffmann-Liste — für Institutionen",
    status: "in Vorbereitung",
    motto: "Jede Platte, jeder Name, jede Geschichte.",
    never: "Nie vergessen.",
    disclaimer: "Arbeitsfassung vom 7. November 2026 für Gespräche mit Institutionen. Nicht veröffentlicht. Keine Trägerschaft als gemeinnützige Organisation. Keine Partnerschaft ist geschlossen.",
    "h-what": "Worum es geht",
    "p-what": "Die Kauffmann-Liste ist eine freie, nicht kommerzielle Karte der Stolpersteine in Deutschland. Eine Familie soll von überall einen Vornamen, einen Nachnamen oder eine Adresse suchen und die Platte vor dem Haus sehen können, samt dem, was wir belegt haben. Nicht mehr.",
    "h-who": "Wer",
    "p-who": "Begründet von Carlos Kauffmann. Eine weitere Biografie veröffentlichen wir hier nicht: dafür fehlt eine Quelle, und wir erfinden keine.",
    "h-today": "Was heute steht",
    "p-today": "Zahlen vom 7. November 2026. Quelle der Steine: OpenStreetMap, ODbL, Auszug 4. November 2026, und Wikidata, CC0. Die Karte ist unvollständig. Die Stiftung Spuren – Gunter Demnig zählt mehr als 116.000 Stolpersteine in 31 Ländern; in offenen Daten zu Deutschland fehlen schätzungsweise 40.000.",
    "cap-stones": "Steine auf der Karte",
    "cap-photos": "mit Foto auf Wikimedia Commons (78,4 %)",
    "cap-text": "mit Biografietext auf der Karte",
    "cap-link": "nur mit Link, ohne Text",
    "cap-none": "ohne Text und ohne solchen Link",
    "cap-insc": "mit Inschrift, unverändert gezeigt",
    "p-bio": "Der Biografietext stammt nur aus den deutschen Wikipedia-Listen „Liste der Stolpersteine in …“, CC BY-SA 4.0, und nur wenn Name, Ort und Adresse oder Dateiname des Fotos übereinstimmen und genau eine Zeile passt. Unsichere Treffer werden nicht gezeigt. In denselben Listen wurden rund 9.900 Texte mit mindestens 300 Zeichen gemessen; die strengere Zuordnung ergibt die 4.038 auf der Karte. Texte von Initiativen werden nicht kopiert.",
    "p-links": "Als Link, nicht als Text: 10.730 Seiten von Stolpersteine Berlin, 7.518 von Stolpersteine Hamburg, 823 von Stolpersteine Bremen, dazu 5.880 Gedenkbuch-IDs, 378 Yad-Vashem-IDs und 1.595 USHMM-IDs aus Wikidata. Arolsen bleibt eine Suche, kein übernommener Bestand.",
    "p-1945": "1945 gibt es auf der Karte nur für Bremerhaven: Luftbild 1945, Monat nicht belegt, CC BY 4.0, neben dem DOP10 von 2025. Berlin 1953, Nordrhein-Westfalen ab 1951 und Dresden 1953 werden nicht als 1945 bezeichnet.",
    "p-hoy": "„Heute“ sind amtliche Orthofotos der Länder, bei denen am 7. November 2026 ein GetMap-Bild und CORS bestätigt wurden. DOP10 in Bremen, Bremerhaven und Nordrhein-Westfalen; sonst überwiegend DOP20. Rheinland-Pfalz antwortet ohne CORS und wird nicht gezeichnet. Schleswig-Holstein und Sachsen-Anhalt nur über https. Weit herausgezoomt liegt Sentinel-2 von 2016 darunter, etwa 10 m, als Übersicht beschriftet, nicht als heutiges Orthofoto.",
    "h-see": "So sieht die Karte aus",
    "cap-overview": "Deutschland, goldene Säulen. Jede Säule ist ein Stein, nicht ein Gebäude von 1945.",
    "cap-compare": "Bremerhaven: Luftbild 1945 und DOP10 2025, dieselbe Stelle.",
    "cap-street": "Berlin, DOP20 Frühjahr 2025, mit den Säulen der heutigen Steine.",
    "cap-video": "Rundgang, 83 Sekunden, lokal aufgenommen. Kein Sendeton.",
    "h-principles": "Grundsätze",
    pr1: "Frei und nicht kommerziell. Kein Eintritt, kein Verkauf der Daten.",
    pr2: "Keine erfundene und keine umgeschriebene Biografie. Kein Text aus einem Sprachmodell.",
    pr3: "Jede Angabe mit Quelle. Was keine Quelle hat, erscheint nicht.",
    pr4: "Die Inschrift steht so, wie sie gegossen ist, einschließlich der Schreibung.",
    pr5: "Familien können korrigieren und um Entfernung bitten. Das Formular ist noch nicht geöffnet.",
    pr6: "Lizenzen und Namensnennung bleiben sichtbar: ODbL, CC0, CC BY-SA, CC BY, Datenlizenz Deutschland, und die Bedingungen jedes Landesamts.",
    pr7: "Geschützte Archive werden verlinkt, nicht kopiert. Anonymisierte Steine bleiben anonym.",
    "h-ask": "Was wir bitten",
    ask1: "Erlaubnis, einen belegten Auszug einer Biografie zu zeigen, mit Autorennamen und Link auf die Originalseite. Oder nur die Erlaubnis zu verlinken.",
    ask2: "Georeferenzierte Luftbilder von 1945 mit geklärter Lizenz. Spätere Jahrgänge übernehmen wir nicht unter der Jahreszahl 1945.",
    ask3: "3D-Modelle und Fotos nur mit offener Lizenz, Fotos vorzugsweise über Wikimedia Commons.",
    ask4: "Menschen, die eine zweite Prüfung machen: Quelle gegen Angabe. Nicht, um Geschichten zu schreiben.",
    ask5: "Eine Ansprechperson für Korrekturen.",
    "h-attr": "So würde die Namensnennung aussehen",
    "p-attr": "Wenn eine Initiative einen Auszug freigibt, steht er in der Karteikarte unter „Die Geschichte“, und mit diesem sichtbaren Nachweis. Ohne diesen Kasten kein Text.",
    "sample-k": "Text",
    sample: "„…der freigegebene Satz, wortgetreu…“",
    "sample-src": "Quelle: Name der Institution, Titel der Seite, URL, Datum der Freigabe. Angezeigt mit Genehmigung. Lizenz: wie vereinbart.",
    "h-contact": "Kontakt",
    "contact-empty": "E-Mail: noch nicht festgelegt.",
    "contact-note": "Eine Adresse, eingetragen an genau einer Stelle im Skript.",
    "h-pdf": "Kurzfassung",
    "p-pdf": "Eine Seite, zum Weitergeben. Dieselben Grenzen wie diese Seite: in Vorbereitung, keine Partnerschaft, keine erfundenen Zahlen.",
    "pdf-de": "PDF auf Deutsch",
    "pdf-en": "PDF in English",
    back: "Zurück zur Karte"
  },
  en: {
    title: "Kauffmann List — for institutions",
    status: "in preparation",
    motto: "Every plaque, every name, every story.",
    never: "Never forget.",
    disclaimer: "Working draft of 7 November 2026 for conversations with institutions. Not published. No organisation claims charitable status here. No partnership has been agreed.",
    "h-what": "What this is",
    "p-what": "The Kauffmann List is a free, non-commercial map of the Stolpersteine in Germany. A family anywhere should be able to search a first name, a surname or an address and see the plaque in front of the house, together with what we can source. Nothing beyond that.",
    "h-who": "Who",
    "p-who": "Founded by Carlos Kauffmann. We do not publish a longer biography here: there is no source for one on this page, and we do not invent one.",
    "h-today": "What exists today",
    "p-today": "Figures of 7 November 2026. The stones come from OpenStreetMap, ODbL, extract of 4 November 2026, and Wikidata, CC0. The map is incomplete. Stiftung Spuren – Gunter Demnig counts more than 116,000 Stolpersteine in 31 countries; open data for Germany are short by an estimated 40,000.",
    "cap-stones": "stones on the map",
    "cap-photos": "with a Wikimedia Commons photo (78.4%)",
    "cap-text": "with a biography text on the map",
    "cap-link": "link only, no text",
    "cap-none": "no text and no such link",
    "cap-insc": "with the inscription, shown as cast",
    "p-bio": "Biography text comes only from the German Wikipedia lists “Liste der Stolpersteine in …”, CC BY-SA 4.0, and only when the name, the place, and the address or the photo filename agree, and only one row matches. Uncertain matches are not shown. Those lists contain about 9,900 texts of at least 300 characters; the stricter match is the 4,038 on the map. Texts from local initiatives are not copied.",
    "p-links": "As links, not as text: 10,730 pages from Stolpersteine Berlin, 7,518 from Stolpersteine Hamburg, 823 from Stolpersteine Bremen, plus 5,880 Gedenkbuch IDs, 378 Yad Vashem IDs and 1,595 USHMM IDs from Wikidata. Arolsen stays a search, not a copied collection.",
    "p-1945": "1945 on the map exists only for Bremerhaven: aerial photograph of 1945, month not documented, CC BY 4.0, beside the 2025 DOP10. Berlin 1953, North Rhine-Westphalia from 1951 and Dresden 1953 are not labelled 1945.",
    "p-hoy": "“Today” means official state orthophotos for which a GetMap image and CORS were confirmed on 7 November 2026. DOP10 in Bremen, Bremerhaven and North Rhine-Westphalia; mostly DOP20 elsewhere. Rhineland-Palatinate responds without CORS and is not drawn. Schleswig-Holstein and Saxony-Anhalt only over https. Zoomed out, Sentinel-2 from 2016 sits underneath, about 10 m, labelled as an overview, not as a current orthophoto.",
    "h-see": "What the map looks like",
    "cap-overview": "Germany, golden columns. Each column is a stone, not a building from 1945.",
    "cap-compare": "Bremerhaven: 1945 aerial photograph and 2025 DOP10, the same place.",
    "cap-street": "Berlin, DOP20 spring 2025, with the columns of today’s stones.",
    "cap-video": "Walkthrough, 83 seconds, recorded locally. No narration.",
    "h-principles": "Principles",
    pr1: "Free and non-commercial. No fee, no sale of the data.",
    pr2: "No invented biography and no rewritten one. No text from a language model.",
    pr3: "Every statement has a source. What has no source is not shown.",
    pr4: "The inscription is shown as cast, including the spelling.",
    pr5: "Families can correct a record and ask for something to be removed. The form is not open yet.",
    pr6: "Licences and attribution stay visible: ODbL, CC0, CC BY-SA, CC BY, the German data licence, and each state survey’s terms.",
    pr7: "Protected archives are linked, not copied. Anonymised stones stay anonymous.",
    "h-ask": "What we ask",
    ask1: "Permission to show a sourced excerpt of a biography, with the author’s name and a link to the original page. Or permission to link only.",
    ask2: "Georeferenced aerial photographs from 1945 with a clear licence. Later years are not presented as 1945.",
    ask3: "3D models and photographs only under an open licence; photographs preferably via Wikimedia Commons.",
    ask4: "People who check a source against a statement. Not people to write stories.",
    ask5: "A person to write to about corrections.",
    "h-attr": "How the credit would look",
    "p-attr": "If an initiative releases an excerpt, it appears on the record under “Their story”, with this visible credit. No credit, no text.",
    "sample-k": "Text",
    sample: "“…the released sentence, word for word…”",
    "sample-src": "Source: name of the institution, title of the page, URL, date of permission. Shown with permission. Licence: as agreed.",
    "h-contact": "Contact",
    "contact-empty": "Email: not yet set.",
    "contact-note": "One address, typed in exactly one place in the script.",
    "h-pdf": "One-page summary",
    "p-pdf": "One page, to pass on. The same limits as this page: in preparation, no partnership, no invented figures.",
    "pdf-de": "PDF in German",
    "pdf-en": "PDF in English",
    back: "Back to the map"
  },
  es: {
    title: "Lista Kauffmann — para instituciones",
    status: "en preparación",
    motto: "Cada placa, cada nombre, cada historia.",
    never: "Nunca olvidar.",
    disclaimer: "Borrador de trabajo del 7 de noviembre de 2026 para conversar con instituciones. No publicado. No hay estatuto de entidad sin ánimo de lucro. No hay ningún acuerdo de colaboración.",
    "h-what": "De qué se trata",
    "p-what": "La Lista Kauffmann es un mapa libre y no comercial de las Stolpersteine en Alemania. Una familia, desde cualquier lugar, debe poder buscar un nombre, un apellido o una dirección y ver la placa frente a la casa, con lo que podamos citar. Nada más.",
    "h-who": "Quién",
    "p-who": "La inició Carlos Kauffmann. No publicamos aquí una biografía más larga: no hay fuente para ello en esta página, y no inventamos una.",
    "h-today": "Lo que hay hoy",
    "p-today": "Cifras del 7 de noviembre de 2026. Las placas vienen de OpenStreetMap, ODbL, extracto del 4 de noviembre de 2026, y de Wikidata, CC0. El mapa está incompleto. La Stiftung Spuren – Gunter Demnig cuenta más de 116.000 Stolpersteine en 31 países; en los datos abiertos de Alemania faltan unas 40.000.",
    "cap-stones": "placas en el mapa",
    "cap-photos": "con foto en Wikimedia Commons (78,4 %)",
    "cap-text": "con texto biográfico en el mapa",
    "cap-link": "solo con enlace, sin texto",
    "cap-none": "sin texto y sin ese enlace",
    "cap-insc": "con inscripción, tal como está grabada",
    "p-bio": "El texto biográfico sale solo de las listas alemanas de Wikipedia «Liste der Stolpersteine in …», CC BY-SA 4.0, y solo si coinciden el nombre, el lugar y la dirección o el nombre del archivo de la foto, y si encaja una sola fila. Las coincidencias dudosas no se muestran. En esas listas se midieron unos 9.900 textos de al menos 300 caracteres; el cruce más estricto es el de las 4.038 que aparecen en el mapa. No copiamos los textos de las iniciativas.",
    "p-links": "Como enlace, no como texto: 10.730 páginas de Stolpersteine Berlin, 7.518 de Stolpersteine Hamburg, 823 de Stolpersteine Bremen, más 5.880 identificadores del Gedenkbuch, 378 de Yad Vashem y 1.595 del USHMM, desde Wikidata. Arolsen sigue siendo un buscador, no un fondo copiado.",
    "p-1945": "1945 en el mapa solo existe para Bremerhaven: fotografía aérea de 1945, mes no documentado, CC BY 4.0, junto al DOP10 de 2025. Berlín 1953, Renania del Norte-Westfalia desde 1951 y Dresde 1953 no se rotulan como 1945.",
    "p-hoy": "«Hoy» son las ortofotos oficiales de los Länder para las que el 7 de noviembre de 2026 se confirmó una imagen GetMap y CORS. DOP10 en Bremen, Bremerhaven y Renania del Norte-Westfalia; en los demás, sobre todo DOP20. Renania-Palatinado responde sin CORS y no se dibuja. Schleswig-Holstein y Sajonia-Anhalt solo por https. Al alejar, debajo está Sentinel-2 de 2016, unos 10 m, rotulado como vista general, no como ortofoto actual.",
    "h-see": "Así se ve el mapa",
    "cap-overview": "Alemania, columnas doradas. Cada columna es una placa, no un edificio de 1945.",
    "cap-compare": "Bremerhaven: fotografía aérea de 1945 y DOP10 de 2025, el mismo lugar.",
    "cap-street": "Berlín, DOP20 primavera de 2025, con las columnas de las placas de hoy.",
    "cap-video": "Recorrido, 83 segundos, grabado en local. Sin narración.",
    "h-principles": "Principios",
    pr1: "Libre y no comercial. Sin entrada, sin venta de los datos.",
    pr2: "Ninguna biografía inventada ni reescrita. Ningún texto de un modelo de lenguaje.",
    pr3: "Cada dato con su fuente. Lo que no tiene fuente no aparece.",
    pr4: "La inscripción se muestra tal como está fundida, incluida la ortografía.",
    pr5: "Las familias pueden corregir y pedir que se retire un dato. El formulario aún no está abierto.",
    pr6: "Las licencias y la atribución siguen visibles: ODbL, CC0, CC BY-SA, CC BY, la licencia de datos alemana y las condiciones de cada servicio cartográfico.",
    pr7: "Los archivos protegidos se enlazan, no se copian. Las placas anonimizadas siguen anónimas.",
    "h-ask": "Lo que pedimos",
    ask1: "Permiso para mostrar un fragmento citado de una biografía, con el nombre de quien lo escribió y un enlace a la página original. O solo permiso para enlazar.",
    ask2: "Fotografías aéreas georreferenciadas de 1945 con la licencia clara. Los años posteriores no se presentan como 1945.",
    ask3: "Modelos 3D y fotos solo con licencia abierta; las fotos, a ser posible, en Wikimedia Commons.",
    ask4: "Personas que comprueben una fuente contra un dato. No personas que escriban historias.",
    ask5: "Una persona de contacto para las correcciones.",
    "h-attr": "Así se vería la atribución",
    "p-attr": "Si una iniciativa autoriza un fragmento, aparece en la ficha bajo «Su historia», con esta cita visible. Sin esa cita, no hay texto.",
    "sample-k": "Texto",
    sample: "«…la frase autorizada, palabra por palabra…»",
    "sample-src": "Fuente: nombre de la institución, título de la página, URL, fecha de la autorización. Mostrado con permiso. Licencia: la acordada.",
    "h-contact": "Contacto",
    "contact-empty": "Correo: aún no está fijado.",
    "contact-note": "Una sola dirección, escrita en un único lugar del programa.",
    "h-pdf": "Resumen de una página",
    "p-pdf": "Una página, para pasar. Los mismos límites que esta: en preparación, sin colaboración acordada, sin cifras inventadas.",
    "pdf-de": "PDF en alemán",
    "pdf-en": "PDF en inglés",
    back: "Volver al mapa"
  }
};

function apply(lang){
  if (!COPY[lang]) lang = "de";
  const t = COPY[lang];
  document.documentElement.lang = lang;
  document.title = t.title;
  document.querySelectorAll("[data-i18n]").forEach(el => {
    const v = t[el.dataset.i18n];
    if (typeof v === "string") el.textContent = v;
  });
  document.querySelectorAll(".lang button").forEach(b => b.setAttribute("aria-pressed", b.dataset.lang === lang ? "true" : "false"));
  const line = document.getElementById("contactLine");
  if (line){
    line.replaceChildren();
    if (CONTACT_EMAIL){
      const a = document.createElement("a");
      a.href = "mailto:" + CONTACT_EMAIL;
      a.textContent = CONTACT_EMAIL;
      line.append(a);
    } else {
      line.textContent = t["contact-empty"];
    }
  }
  try { localStorage.setItem("kauffmann.proyectoLang", lang); } catch (e) {}
}

const q = new URLSearchParams(location.search).get("lang");
let initial = q || "de";
if (!q){
  try { initial = localStorage.getItem("kauffmann.proyectoLang") || "de"; } catch (e) {}
}
apply(initial);
document.querySelectorAll(".lang button").forEach(b => b.addEventListener("click", () => apply(b.dataset.lang)));
