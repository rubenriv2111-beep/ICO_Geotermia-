<!DOCTYPE qgis PUBLIC 'http://mrcc.com/qgis.dtd' 'SYSTEM'>
<qgis styleCategories='AllStyleCategories' version='3.44.15' hasScaleBasedVisibilityFlag='0' minScale='1e+08' maxScale='0'>
  <pipe>
    <provider>
      <resampling maxOversampling='2' zoomedOutResamplingMethod='bilinear' zoomedInResamplingMethod='bilinear' enabled='false'/>
    </provider>
    <rasterrenderer alphaBand='-1' classificationMax='125' classificationMin='-625' opacity='1' band='1' type='singlebandpseudocolor'>
      <rasterTransparency>
        <singleValuePixelList>
          <pixelListEntry min='-99999' max='-99999' percentTransparent='100'/>
        </singleValuePixelList>
      </rasterTransparency>
      <rastershader>
        <colorrampshader maximumValue='125' labelPrecision='0' clip='0' colorRampType='DISCRETE' minimumValue='-625'>
          <item alpha='255' value='-600.0' label='-625 nT (Bajo Extremo)' color='#04b4e6'/>
          <item alpha='255' value='-550.0' label='-550 nT' color='#5ac4ea'/>
          <item alpha='255' value='-500.0' label='-500 nT' color='#82cfeb'/>
          <item alpha='255' value='-450.0' label='-450 nT' color='#a6d7e2'/>
          <item alpha='255' value='-400.0' label='-400 nT' color='#cbe8dd'/>
          <item alpha='255' value='-350.0' label='-350 nT' color='#dfefde'/>
          <item alpha='255' value='-300.0' label='-300 nT' color='#e3f2e7'/>
          <item alpha='255' value='-250.0' label='-250 nT' color='#f0f7e7'/>
          <item alpha='255' value='-200.0' label='-200 nT' color='#fffcdf'/>
          <item alpha='255' value='-150.0' label='-150 nT' color='#fffbd2'/>
          <item alpha='255' value='-100.0' label='-100 nT' color='#ffeebc'/>
          <item alpha='255' value='-50.0' label='-50 nT' color='#ffe4b8'/>
          <item alpha='255' value='0.0' label='0 nT' color='#fdd1b0'/>
          <item alpha='255' value='50.0' label='+50 nT' color='#faad7c'/>
          <item alpha='255' value='100.0' label='+100 nT' color='#f89b5c'/>
          <item alpha='255' value='150.0' label='+125 nT (Alto Extremo)' color='#f58345'/>
        </colorrampshader>
      </rastershader>
    </rasterrenderer>
    <brightnesscontrast brightness='0' contrast='0' gamma='1'/>
  </pipe>
  <blendMode>0</blendMode>
</qgis>