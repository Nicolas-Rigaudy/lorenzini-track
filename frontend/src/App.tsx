import { useEffect, useMemo, useState } from 'react'
import { MapView } from './components/MapView'
import { StudiesPanel } from './components/StudiesPanel'
import { SpeciesPanel } from './components/SpeciesPanel'
import { Header, HEADER_HEIGHT } from './components/Header'
import { Legend } from './components/Legend'
import { TimeFilter } from './components/TimeFilter'
import { TaxonFilter } from './components/TaxonFilter'
import { fetchStudies } from './dataSource'
import type { Study } from './types'
import { fetchSpeciesList, type SpeciesListItem } from './speciesApi'
import { buildSpeciesColors } from './speciesColors'
import { DEFAULT_TAXON_GROUP, speciesInGroup, studiesInGroup, taxonOptions } from './taxa'

function App() {
  const [studies, setStudies] = useState<Study[]>([])
  const [studiesLoading, setStudiesLoading] = useState(true)
  const [speciesList, setSpeciesList] = useState<SpeciesListItem[]>([])
  const [speciesLoading, setSpeciesLoading] = useState(true)
  const [taxonGroup, setTaxonGroup] = useState(DEFAULT_TAXON_GROUP)
  const [selectedStudyId, setSelectedStudyId] = useState<number | null>(null)
  const [selectedSpeciesName, setSelectedSpeciesName] = useState<string | null>(null)
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    const saved = localStorage.getItem('lorenzini-track-theme')
    if (saved === 'light' || saved === 'dark') return saved
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
  })

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('lorenzini-track-theme', theme)
  }, [theme])

  useEffect(() => {
    fetchStudies().then((data) => {
      setStudies(data)
      setStudiesLoading(false)
    })
    fetchSpeciesList().then((list) => {
      setSpeciesList(list)
      setSpeciesLoading(false)
    })
  }, [])

  // Colours come from the full list so a species keeps its colour whatever the filter.
  const speciesColors = useMemo(() => buildSpeciesColors(speciesList), [speciesList])

  // Sharks by default; the taxon filter narrows the gallery, map pins, studies and legend.
  const taxa = useMemo(() => taxonOptions(speciesList), [speciesList])
  const visibleSpecies = useMemo(() => speciesInGroup(speciesList, taxonGroup), [speciesList, taxonGroup])
  const visibleStudies = useMemo(
    () => studiesInGroup(studies, speciesList, taxonGroup),
    [studies, speciesList, taxonGroup],
  )

  const yearBounds = useMemo<[number, number] | null>(() => {
    const years: number[] = []
    for (const s of visibleStudies) {
      if (s.date_range.start) years.push(Number(s.date_range.start.slice(0, 4)))
      if (s.date_range.end) years.push(Number(s.date_range.end.slice(0, 4)))
    }
    return years.length ? [Math.min(...years), Math.max(...years)] : null
  }, [visibleStudies])

  const [selectedYears, setSelectedYears] = useState<[number, number] | null>(null)
  useEffect(() => {
    if (yearBounds && !selectedYears) setSelectedYears(yearBounds)
  }, [yearBounds, selectedYears])

  // Only filter the map when the window is narrower than the full span.
  const yearRange =
    selectedYears && yearBounds && (selectedYears[0] !== yearBounds[0] || selectedYears[1] !== yearBounds[1])
      ? selectedYears
      : null

  // Gallery → profile (and back). Selecting a species shows all of its occurrences on the map.
  // Switching family goes back to the overview and resets the time window to its span.
  function selectTaxonGroup(group: string) {
    setTaxonGroup(group)
    setSelectedSpeciesName(null)
    setSelectedStudyId(null)
    setSelectedYears(null)
  }

  function selectSpecies(name: string | null) {
    setSelectedSpeciesName(name)
    setSelectedStudyId(null)
  }

  // Selecting a study from the left list: a single-species study opens that species' page with
  // this study focused (so the map shows THIS study's fixes and the study's details are shown),
  // while a multi-species study shows the whole study and lets you pick a species.
  function selectStudy(studyId: number | null) {
    if (studyId === null) {
      setSelectedStudyId(null)
      setSelectedSpeciesName(null)
      return
    }
    const study = studies.find((s) => s.id === studyId)
    setSelectedStudyId(studyId)
    setSelectedSpeciesName(study && study.species.length === 1 ? study.species[0] : null)
  }

  // Focusing a study from inside a species profile keeps the species selected, so the map
  // shows just that species within that study.
  function focusStudy(studyId: number | null) {
    setSelectedStudyId(studyId)
  }

  // When a multi-species study is selected (and no species yet), narrow the gallery to that
  // study's species.
  const studySpecies =
    selectedStudyId && !selectedSpeciesName
      ? (studies.find((s) => s.id === selectedStudyId)?.species ?? null)
      : null

  return (
    <div style={{ height: '100%', width: '100%', display: 'flex', flexDirection: 'column' }}>
      <Header theme={theme} onToggleTheme={() => setTheme((t) => (t === 'dark' ? 'light' : 'dark'))}>
        <TaxonFilter options={taxa} value={taxonGroup} onChange={selectTaxonGroup} />
      </Header>
      <div style={{ position: 'relative', flex: 1, height: `calc(100% - ${HEADER_HEIGHT}px)` }}>
        <MapView
          selectedStudyId={selectedStudyId}
          selectedSpeciesName={selectedSpeciesName}
          speciesColors={speciesColors}
          theme={theme}
          yearRange={yearRange}
          speciesList={visibleSpecies}
          onPickSpecies={selectSpecies}
        />
        <StudiesPanel
          studies={visibleStudies}
          loading={studiesLoading || speciesLoading}
          selectedStudyId={selectedStudyId}
          onSelectStudy={selectStudy}
          onSelectSpecies={selectSpecies}
        />
        <SpeciesPanel
          speciesList={visibleSpecies}
          speciesColors={speciesColors}
          studySpecies={studySpecies}
          selectedSpeciesName={selectedSpeciesName}
          onSelectSpecies={selectSpecies}
          studies={studies}
          selectedStudyId={selectedStudyId}
          onSelectStudy={focusStudy}
        />
        <Legend species={visibleSpecies} speciesColors={speciesColors} />
        {yearBounds && selectedYears && yearBounds[0] !== yearBounds[1] && (
          <TimeFilter bounds={yearBounds} value={selectedYears} onChange={setSelectedYears} />
        )}
      </div>
    </div>
  )
}

export default App
