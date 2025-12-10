import React, { useEffect, useRef, useState } from "react";
import "ol/ol.css";

import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import VectorSource from "ol/source/Vector";
import Feature from "ol/Feature";
import Point from "ol/geom/Point";
import LineString from "ol/geom/LineString";
import VectorLayer from "ol/layer/Vector";
import { fromLonLat } from "ol/proj";
import { Stroke, Style, Circle as CircleStyle, Fill } from "ol/style";

function rsrpToColor(rsrp) {
  if (rsrp > -80) return "green";
  if (rsrp > -95) return "yellow";
  if (rsrp > -110) return "orange";
  return "red";
}

function App() {
  const mapRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const [data, setData] = useState([]);

  useEffect(() => {
    fetch("https://base.server.cloud-ip.cc/api")
      .then((res) => res.json())
      .then((json) => {
        setData(json);
      })
      .catch(console.error);
  }, []);

  useEffect(() => {
    if (!data.length) return;
    if (mapInstanceRef.current) return;

    const coords = data.map((p) => fromLonLat([p.longitude, p.latitude]));
    const line = new LineString(coords);

    const pointFeature = data.map(
      (p) =>
        new Feature({
          geometry: new Point(fromLonLat([p.longitude, p.latitude])),
          rsrp: p.rsrp,
        })
    );

    const lineFeature = new Feature({ geometry: line });

    const lineLayer = new VectorLayer({
      source: new VectorSource({
        features: [lineFeature, ...pointFeature],
      }),
      style: (feature) => {
        const geom = feature.getGeometry();
        if (geom instanceof LineString) {
          return new Style({
            stroke: new Stroke({
              color: "black",
              width: 2,
            }),
          });
        }

        const rsrp = feature.get("rsrp");
        const color = rsrp !== undefined ? rsrpToColor(rsrp) : "gray";

        return new Style({
          image: new CircleStyle({
            radius: 5,
            fill: new Fill({ color }),
          }),
        });
      },
    });

    const savedCenter = JSON.parse(localStorage.getItem("mapCenter")) || [0, 0];
    const savedZoom = JSON.parse(localStorage.getItem("mapZoom")) || 2;

    mapInstanceRef.current = new Map({
      target: mapRef.current,
      layers: [
        new TileLayer({
          source: new OSM(),
          preload: 2,
        }),
        lineLayer,
      ],
      view: new View({
        center: savedCenter,
        zoom: savedZoom,
      }),
    });

    const map = mapInstanceRef.current;

    const onMoveEnd = () => {
      const view = map.getView();
      localStorage.setItem("mapCenter", JSON.stringify(view.getCenter()));
      localStorage.setItem("mapZoom", JSON.stringify(view.getZoom()));
    };
    map.on("moveend", onMoveEnd);

    return () => {
      map.un("moveend", onMoveEnd);
      map.setTarget(null);
      mapInstanceRef.current = null;
    };
  }, [data]);

  return (
    <main className="ml-16 p-4 scrollbar-width-none">
      <div style={{ width: "100%", height: "100vh" }}>
        <div ref={mapRef} style={{ width: "100%", height: "100%" }}></div>
      </div>
    </main>
  );
}

export default App;
