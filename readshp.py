from osgeo import gdal, ogr, osr
import os
import re


def ReadVectorFile(infilename, outfilename):
    gdal.AllRegister()
    ogr.RegisterAll()
    gdal.SetConfigOption("GDAL_FILENAME_IS_UTF8", "NO")
    gdal.SetConfigOption("SHAPE_ENCODING", "CP936")

    driver = ogr.GetDriverByName('ESRI Shapefile')

    ds = driver.Open(infilename, 0)
    # print(dir(ds))
    if ds is None:
        print("打开文件" + str(infilename) + "失败")
        return
    print('成功打开文件')

    if os.path.exists(outfilename):
        driver.DeleteDataSource(outfilename)
    outds = driver.CreateDataSource(outfilename)
    inlayer = ds.GetLayer()
    spatial = inlayer.GetSpatialRef()
    # 坐标系转换
    # outosr = osr.SpatialReference()
    # outosr.ImportFromEPSG(3857)
    # trans = osr.CoordinateTransformation(spatial, outosr)
    outlayer = outds.CreateLayer('samChina', spatial, geom_type=ogr.wkbPolygon)
    feature = inlayer.GetFeature(0)  # 读取一个要素，以便获取表头信息
    infieldcount = feature.GetFieldCount()
    for attr in range(infieldcount):
        infielddefn = feature.GetFieldDefnRef(attr)
        # print(infielddefn.GetName())  # 输出输入矢量的所有字段名称
        outlayer.CreateField(infielddefn)

    inlayer.ResetReading()
    # 遍历所有要素，开始读取和写入
    feature = inlayer.GetNextFeature()

    # print(dir(feature))
    while feature:
        # # 读取ID、cover字段值
        # id = feature.GetFieldAsString('CAPITAL')
        # cover = feature.GetFieldAsString('COUNTRY')
        # 获取要素几何
        geom = feature.GetGeometryRef()
        # print(dir(geom))
        box1 = ogr.Geometry(ogr.wkbLinearRing)
        oDefn = outlayer.GetLayerDefn()  # 定义要素
        oFeatureTriangle = ogr.Feature(oDefn)
        intersecoFeatureTriangle = ogr.Feature(oDefn)
        for i in geom:
            c = i.ExportToWkt()
            pattern = re.compile('LINEARRING \((.*)\)')
            find = pattern.search(c)
            if find is not None:
                # print('aaaaaaa')
                xyline = str(find.group(1))
                # print(type(xyline))
                xy = xyline.split(",")
                p = 0

                # xory1 = xy[0].split(" ")
                # x1 = float(xory1[0])
                # y1 = float(xory1[1])
                for t in xy:
                    if p % 2 == 0:
                        xory = t.split(" ")
                        box1.AddPoint(float(xory[0]), float(xory[1]))
                    p += 1
                # box1.AddPoint(x1, y1)

                garden1 = ogr.Geometry(ogr.wkbPolygon)  # 每次重新定义单多变形
                garden1.AddGeometry(box1)  # 将轮廓坐标放在单多边形中
                garden1.CloseRings()
                geomTriangle = ogr.CreateGeometryFromWkt(str(garden1))  # 将封闭后的多边形集添加到属性表
                oFeatureTriangle.SetGeometry(geomTriangle)
                intersec = garden1.Difference(geom)
                interscgeomTriangle = ogr.CreateGeometryFromWkt(str(intersec))  # 将封闭后的多边形集添加到属性表
                intersecoFeatureTriangle.SetGeometry(interscgeomTriangle)
                outlayer.CreateFeature(oFeatureTriangle)
                # outlayer.CreateFeature(intersecoFeatureTriangle)
            # else:
            #     print(c)
            #     print('aaaaaaaaaaaaaaaa')
            #     pattern = re.compile('POLYGON \(\((.*)\)\)')
            #     find = pattern.search(c)
            #     xyplg = str(find.group(1))
            #     xy = xyplg.split(",")
            #     p = 0
            #     xory1 = xy[0].split(" ")
            #     x1 = float(xory1[0])
            #     y1 = float(xory1[1])
            #     for t in xy:
            #         if p % 2 == 0:
            #             xory = t.split(" ")
            #             box1.AddPoint(float(xory[0]), float(xory[1]))
            #         p += 1
            #     box1.AddPoint(x1, y1)
            #
            #     garden1 = ogr.Geometry(ogr.wkbPolygon)  # 每次重新定义单多变形
            #     garden1.AddGeometry(box1)  # 将轮廓坐标放在单多边形中
            #
            #     geomTriangle = ogr.CreateGeometryFromWkt(str(garden1))  # 将封闭后的多边形集添加到属性表
            #     oFeatureTriangle.SetGeometry(geomTriangle)
            #     intersec = garden1.Difference(geom)
            #     interscgeomTriangle = ogr.CreateGeometryFromWkt(str(intersec))  # 将封闭后的多边形集添加到属性表
            #     intersecoFeatureTriangle.SetGeometry(interscgeomTriangle)
            #     # outlayer.CreateFeature(oFeatureTriangle)
            #     outlayer.CreateFeature(intersecoFeatureTriangle)


        # 清除缓存并获取下一个要素
        feature.Destroy()
        feature = inlayer.GetNextFeature()



    # outlayer.CreateFeature(intersec)



    # outfielddefn = outlayer.GetLayerDefn()

    # inlayer.SetAttributeFilter("\"FID\"=41")

    # 读取属性表数据
    # oDefn = oLayer.GetLayerDefn()
    # iFieldCount = oDefn.GetFieldCount()
    # for iAttr in range(iFieldCount):
    #     oField = oDefn.GetFieldDefn(iAttr)
    #     print("%s: %s(%d.%d)" % (
    #         oField.GetNameRef(),
    #         oField.GetFieldTypeName(oField.GetType()),
    #         oField.GetWidth(),
    #         oField.GetPrecision()))

    # print("要素个数 = " + str(oLayer.GetFeatureCount()))

    # feature = inlayer.GetFeature(41)
    # # print(dir(feature))
    # # featureFID = feature.GetFID
    # # print(str(featureFID))
    # featureGRef = feature.GetGeometryRef()
    # featureGRef.Transform(trans)
    # print(dir(featureGRef))
    # # a = featureGRef.ExportToWkt()
    # # print(str(a))
    # # featureExRing = featureGRef.getExteriorRing()
    # # print(str(featureExRing))
    # #
    # outfeature = ogr.Feature(outfielddefn)
    # #
    # outfeature.SetGeometry(featureGRef)
    # # # outfeature.SetField('name', infeature.GetField('name'))
    # outlayer.CreateFeature(outfeature)
    #
    # #
    # # featureExtRing = featureGRef.GetGeometryRef(0)
    # # print(str(featureExtRing))
    # # for feat in featureExtRing:
    # #     print(str(feat.GetX()))
    # #     print(str(feat.GetY()))
    #
    # # #删除指定layer
    # # # dl = ds.DeleteLayer(0)
    # # # print(str(dl))
    # #
    # # ds.DestroyDataSource()
    #
    # # 保存投影文件
    # outosr.MorphFromESRI()
    # prjfile = ('samChina6.prj')
    # fn = open(prjfile, 'w')
    # fn.write(outosr.ExportToWkt())
    # fn.close()
    ds.Destroy()
    outds.Destroy()


# 切换到目标路径
os.chdir(r'H:\zzz')
infilename2 = r"World_region.shp"
outfilename2 = r"samChina14.shp"
# filename2 = r"H:\1zang\影像和矢量\w_project.shp"
ReadVectorFile(infilename2, outfilename2)
