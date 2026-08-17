/**
 * Mapeo de carrera → skills del vocabulario del oráculo.
 *
 * POR QUÉ EXISTE ESTE FICHERO
 * ---------------------------
 * `POST /api/v1/oracle/full_profile` resuelve el campo `skills` contra
 * `oracle/recommendation/data/processed/skills_catalog.csv` usando
 * `_slugify_skill()` (backend/app/services/oracle_catalog.py). Ese vocabulario
 * son 52 skills técnicas en inglés — "Python", "Docker", "Excel"… — mientras
 * que las etiquetas de `CAREERS` son nombres de carrera en español.
 *
 * Enviar las etiquetas directamente resolvía 0 de 50: `resolved_skill_ids`
 * llegaba vacío, `skill_overlap_score` era 0 para todas las simulaciones y el
 * ranking salía sólo de los puntajes psicométricos. Este mapa traduce cada
 * carrera a skills que el catálogo sí reconoce.
 *
 * MANTENIMIENTO
 * -------------
 * Los valores deben coincidir con la columna `skill_name` del CSV (la
 * comparación es por slug, así que mayúsculas y espacios dan igual, pero el
 * nombre tiene que existir). `npm run build` no valida esto: si tocas el
 * catálogo, vuelve a comprobar que todo resuelve.
 *
 * LIMITACIÓN CONOCIDA
 * -------------------
 * El vocabulario no cubre varios dominios (seguridad, arquitectura, música,
 * ingenierías, astronomía). Esas carreras usan la aproximación más cercana
 * disponible, no un mapeo fiel. Ampliar `skills_catalog.csv` es la solución
 * de fondo.
 */

export const CAREER_SKILLS = {
    // ── Tecnología
    cloud: ['Docker', 'Kubernetes', 'AWS', 'Git'],
    software: ['Python', 'JavaScript', 'React', 'Node.js', 'Git'],
    data: ['SQL', 'Data Analysis', 'Python', 'Tableau', 'Statistics'],
    ai: ['Python', 'Machine Learning', 'Deep Learning', 'TensorFlow', 'Statistics'],
    cybersec: ['Docker', 'Git', 'Python', 'AWS'],
    databases: ['SQL', 'MongoDB', 'Python', 'Data Analysis'],
    iot: ['Python', 'Docker', 'AWS', 'Node.js'],
    research: ['Research', 'Statistics', 'Academic Writing', 'R'],

    // ── Negocios
    product: ['Requirements Gathering', 'Business Analysis', 'Strategic Planning', 'Data Analysis'],
    biz: ['Business Analysis', 'Strategic Planning', 'Case Analysis', 'Excel'],
    finance: ['Financial Analysis', 'Financial Modeling', 'Valuation', 'DCF Analysis', 'Excel'],
    marketing: ['Marketing', 'SEO', 'Google Analytics', 'Content Strategy', 'Email Marketing', 'Social Media'],
    intl: ['Strategic Planning', 'Business Analysis', 'Marketing', 'Forecasting'],
    hr: ['Counseling', 'Strategic Planning', 'Business Analysis'],
    logistics: ['Forecasting', 'Excel', 'Data Analysis', 'Budgeting', 'Strategic Planning'],
    ecommerce: ['SEO', 'Google Analytics', 'Marketing', 'Content Creation', 'Social Media'],
    banking: ['Financial Analysis', 'Valuation', 'DCF Analysis', 'Bloomberg Terminal', 'Excel'],
    startup: ['Strategic Planning', 'Business Analysis', 'Marketing', 'Budgeting', 'Financial Modeling'],

    // ── Diseño
    ux: ['Visual Design', 'Adobe Creative Suite', 'Requirements Gathering', 'Research'],
    graphic: ['Visual Design', 'Adobe Creative Suite', 'Brand Management', 'Content Creation'],
    architecture: ['Visual Design', 'Adobe Creative Suite', 'Budgeting', 'Research'],
    interior: ['Visual Design', 'Adobe Creative Suite', 'Budgeting'],
    photo: ['Adobe Creative Suite', 'Visual Design', 'Content Creation', 'Social Media'],
    music: ['Content Creation', 'Adobe Creative Suite', 'Social Media', 'Brand Management'],

    // ── Salud
    medicine: ['Medical Knowledge', 'Patient Care', 'Clinical Assessment', 'Research'],
    nursing: ['Patient Care', 'Clinical Assessment', 'Medical Knowledge', 'Counseling'],
    pharmacy: ['Medical Knowledge', 'Research', 'Clinical Assessment', 'Statistics'],
    psychology: ['Counseling', 'Clinical Assessment', 'Research', 'Academic Writing'],
    nutrition: ['Patient Care', 'Medical Knowledge', 'Counseling', 'Research'],
    physio: ['Patient Care', 'Clinical Assessment', 'Medical Knowledge'],
    optometry: ['Clinical Assessment', 'Patient Care', 'Medical Knowledge'],
    biomedical: ['Research', 'Medical Knowledge', 'Statistics', 'Python', 'Data Analysis'],
    publichealth: ['Research', 'Statistics', 'Data Analysis', 'Grant Writing', 'Medical Knowledge'],

    // ── Ciencias
    bio: ['Research', 'Statistics', 'Academic Writing', 'R', 'Data Analysis'],
    chem: ['Research', 'Statistics', 'Academic Writing', 'Data Analysis'],
    physics: ['Research', 'Statistics', 'Python', 'Academic Writing', 'R'],
    env: ['Research', 'Data Analysis', 'Statistics', 'Grant Writing', 'Academic Writing'],
    astro: ['Research', 'Python', 'Statistics', 'Academic Writing', 'R'],

    // ── Ingeniería
    civil: ['Budgeting', 'Strategic Planning', 'Research', 'Excel'],
    electro: ['Python', 'Research', 'Statistics', 'Excel'],
    mech: ['Research', 'Excel', 'Statistics', 'Budgeting'],
    aero: ['Research', 'Python', 'Statistics', 'Excel'],
    industrial: ['Forecasting', 'Budgeting', 'Data Analysis', 'Excel', 'Strategic Planning'],
    energy: ['Research', 'Forecasting', 'Data Analysis', 'Budgeting'],

    // ── Social
    law: ['Legal Research', 'Legal Writing', 'Case Analysis', 'Academic Writing'],
    journalism: ['Content Creation', 'Content Strategy', 'Social Media', 'Academic Writing'],
    education: ['Pedagogy', 'Curriculum Development', 'Lesson Planning', 'Counseling'],
    polisci: ['Research', 'Academic Writing', 'Legal Research', 'Grant Writing'],
    socialwork: ['Counseling', 'Grant Writing', 'Research', 'Patient Care'],
    tourism: ['Marketing', 'Social Media', 'Content Creation', 'Budgeting'],
}

/**
 * Une, deduplica y recorta las skills de las carreras elegidas.
 * El tope de 100 es el `max_length` de `OracleProfileInput.skills`.
 */
export function getSkillsForCareers(careerIds = []) {
    const out = []
    const seen = new Set()
    for (const id of careerIds) {
        for (const skill of CAREER_SKILLS[id] || []) {
            if (!seen.has(skill)) {
                seen.add(skill)
                out.push(skill)
            }
        }
    }
    return out.slice(0, 100)
}
