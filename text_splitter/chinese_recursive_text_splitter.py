import re
from typing import List, Optional, Any
from langchain.text_splitter import RecursiveCharacterTextSplitter
import logging

logger = logging.getLogger(__name__)


def _split_text_with_regex_from_end(
        text: str, separator: str, keep_separator: bool
) -> List[str]:
    # Now that we have the separator, split the text
    if separator:
        if keep_separator:
            # The parentheses in the pattern keep the delimiters in the result.
            _splits = re.split(f"({separator})", text)
            splits = ["".join(i) for i in zip(_splits[0::2], _splits[1::2])]
            if len(_splits) % 2 == 1:
                splits += _splits[-1:]
            # splits = [_splits[0]] + splits
        else:
            splits = re.split(separator, text)
    else:
        splits = list(text)
    return [s for s in splits if s != ""]


class ChineseRecursiveTextSplitter(RecursiveCharacterTextSplitter):
    def __init__(
            self,
            separators: Optional[List[str]] = None,
            keep_separator: bool = True,
            is_separator_regex: bool = True,
            **kwargs: Any,
    ) -> None:
        """Create a new TextSplitter."""
        super().__init__(keep_separator=keep_separator, **kwargs)
        self._separators = separators or [
            "\n\n",
            "\n",
            "。|！|？",
            "\.\s|\!\s|\?\s",
            "；|;\s",
            "，|,\s"
        ]
        self._is_separator_regex = is_separator_regex

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """Split incoming text and return chunks."""
        final_chunks = []
        # Get appropriate separator to use
        separator = separators[-1]
        new_separators = []
        for i, _s in enumerate(separators):
            _separator = _s if self._is_separator_regex else re.escape(_s)
            if _s == "":
                separator = _s
                break
            if re.search(_separator, text):
                separator = _s
                new_separators = separators[i + 1:]
                break

        _separator = separator if self._is_separator_regex else re.escape(separator)
        splits = _split_text_with_regex_from_end(text, _separator, self._keep_separator)

        # Now go merging things, recursively splitting longer texts.
        _good_splits = []
        _separator = "" if self._keep_separator else separator
        for s in splits:
            if self._length_function(s) < self._chunk_size:
                _good_splits.append(s)
            else:
                if _good_splits:
                    merged_text = self._merge_splits(_good_splits, _separator)
                    final_chunks.extend(merged_text)
                    _good_splits = []
                if not new_separators:
                    final_chunks.append(s)
                else:
                    other_info = self._split_text(s, new_separators)
                    final_chunks.extend(other_info)
        if _good_splits:
            merged_text = self._merge_splits(_good_splits, _separator)
            final_chunks.extend(merged_text)
        return [re.sub(r"\n{2,}", "\n", chunk.strip()) for chunk in final_chunks if chunk.strip()!=""]


if __name__ == "__main__":
    text_splitter = ChineseRecursiveTextSplitter(
        keep_separator=True,
        is_separator_regex=True,
        chunk_size=50,
        chunk_overlap=0
    )
    ls = [
        # """中国对外贸易形势报告（75页）。前 10 个月，一般贸易进出口 19.5 万亿元，增长 25.1%， 比整体进出口增速高出 2.9 个百分点，占进出口总额的 61.7%，较去年同期提升 1.6 个百分点。其中，一般贸易出口 10.6 万亿元，增长 25.3%，占出口总额的 60.9%，提升 1.5 个百分点；进口8.9万亿元，增长24.9%，占进口总额的62.7%， 提升 1.8 个百分点。加工贸易进出口 6.8 万亿元，增长 11.8%， 占进出口总额的 21.5%，减少 2.0 个百分点。其中，出口增 长 10.4%，占出口总额的 24.3%，减少 2.6 个百分点；进口增 长 14.2%，占进口总额的 18.0%，减少 1.2 个百分点。此外， 以保税物流方式进出口 3.96 万亿元，增长 27.9%。其中，出 口 1.47 万亿元，增长 38.9%；进口 2.49 万亿元，增长 22.2%。前三季度，中国服务贸易继续保持快速增长态势。服务 进出口总额 37834.3 亿元，增长 11.6%；其中服务出口 17820.9 亿元，增长 27.3%；进口 20013.4 亿元，增长 0.5%，进口增 速实现了疫情以来的首次转正。服务出口增幅大于进口 26.8 个百分点，带动服务贸易逆差下降 62.9%至 2192.5 亿元。服 务贸易结构持续优化，知识密集型服务进出口 16917.7 亿元， 增长 13.3%，占服务进出口总额的比重达到 44.7%，提升 0.7 个百分点。 二、中国对外贸易发展环境分析和展望 全球疫情起伏反复，经济复苏分化加剧，大宗商品价格 上涨、能源紧缺、运力紧张及发达经济体政策调整外溢等风 险交织叠加。同时也要看到，我国经济长期向好的趋势没有 改变，外贸企业韧性和活力不断增强，新业态新模式加快发 展，创新转型步伐提速。产业链供应链面临挑战。美欧等加快出台制造业回迁计 划，加速产业链供应链本土布局，跨国公司调整产业链供应 链，全球双链面临新一轮重构，区域化、近岸化、本土化、 短链化趋势凸显。疫苗供应不足，制造业“缺芯”、物流受限、 运价高企，全球产业链供应链面临压力。 全球通胀持续高位运行。能源价格上涨加大主要经济体 的通胀压力，增加全球经济复苏的不确定性。世界银行今年 10 月发布《大宗商品市场展望》指出，能源价格在 2021 年 大涨逾 80%，并且仍将在 2022 年小幅上涨。IMF 指出，全 球通胀上行风险加剧，通胀前景存在巨大不确定性。""",
        """
        <table border="1" class="dataframe">
  <tbody>
    <tr>
      <td>姓名</td>
      <td>手机号</td>
      <td>岗位</td>
      <td>班级</td>
    </tr>
    <tr>
      <td>孙金红</td>
      <td>13750891367</td>
      <td>副园长</td>
      <td>荷花塘小班+二班</td>
    </tr>
    <tr>
      <td>陈舒铌</td>
      <td>15868150467</td>
      <td>保教主任</td>
      <td>采荷中班+二班</td>
    </tr>
    <tr>
      <td>童雯</td>
      <td>13666655937</td>
      <td>办公室主任</td>
      <td>采荷大班+七班</td>
    </tr>
    <tr>
      <td>毛信麟</td>
      <td>13758294464</td>
      <td>保教副主任</td>
      <td>荷花塘小班+二班</td>
    </tr>
    <tr>
      <td>姚黎</td>
      <td>13588048001</td>
      <td></td>
      <td>采荷大班+六班</td>
    </tr>
    <tr>
      <td>方梦茹</td>
      <td>15990115069</td>
      <td></td>
      <td>采荷小班+五班</td>
    </tr>
    <tr>
      <td>项露茜</td>
      <td>18757991568</td>
      <td></td>
      <td>采荷小班+七班</td>
    </tr>
    <tr>
      <td>丁敏</td>
      <td>13355815610</td>
      <td></td>
      <td>采荷小班+七班</td>
    </tr>
    <tr>
      <td>陈敏</td>
      <td>13868171133</td>
      <td></td>
      <td>采荷中班+二班</td>
    </tr>
    <tr>
      <td>吴婕</td>
      <td>13575747382</td>
      <td></td>
      <td>采荷大班+三班</td>
    </tr>
    <tr>
      <td>王生芳</td>
      <td>13567144691</td>
      <td></td>
      <td>采荷中班+三班</td>
    </tr>
    <tr>
      <td>林雪</td>
      <td>13588023502</td>
      <td></td>
      <td>采荷中班+七班</td>
    </tr>
    <tr>
      <td>李珍</td>
      <td>15858171798</td>
      <td></td>
      <td>采荷小班+五班</td>
    </tr>
    <tr>
      <td>鲍紫影</td>
      <td>19157797200</td>
      <td></td>
      <td>采荷中班+四班</td>
    </tr>
    <tr>
      <td>虞凯悦</td>
      <td>15088624274</td>
      <td></td>
      <td>采荷小班+六班</td>
    </tr>
    <tr>
      <td>王海博</td>
      <td>18858165431</td>
      <td></td>
      <td>采荷中班+五班</td>
    </tr>
    <tr>
      <td>严婷</td>
      <td>15968174722</td>
      <td></td>
      <td>采荷大班+七班</td>
    </tr>
    <tr>
      <td>章型型</td>
      <td>15605882366</td>
      <td>总务主任</td>
      <td>采荷中班+六班</td>
    </tr>
    <tr>
      <td>陈馨怡</td>
      <td>15957101288</td>
      <td>团支部书记</td>
      <td>采荷小班+六班</td>
    </tr>
    <tr>
      <td>朱建锦</td>
      <td>13588852366</td>
      <td></td>
      <td>采荷中班+七班</td>
    </tr>
    <tr>
      <td>周胜男</td>
      <td>13957171812</td>
      <td></td>
      <td>采荷大班+三班</td>
    </tr>
    <tr>
      <td>朱小吉</td>
      <td>19558133916</td>
      <td></td>
      <td>采荷中班+六班</td>
    </tr>
    <tr>
      <td>崔思佳</td>
      <td>13819267055</td>
      <td></td>
      <td>采荷小班+一班</td>
    </tr>
    <tr>
      <td>唐洁云</td>
      <td>13588481906</td>
      <td></td>
      <td>采荷大班+六班</td>
    </tr>
    <tr>
      <td>庄怡</td>
      <td>18658115878</td>
      <td></td>
      <td>采荷中班+二班</td>
    </tr>
    <tr>
      <td>翁梦杰</td>
      <td>15669061122</td>
      <td></td>
      <td>采荷小班+三班</td>
    </tr>
    <tr>
      <td>陈芳芳</td>
      <td>15825542558</td>
      <td></td>
      <td>采荷中班+四班</td>
    </tr>
    <tr>
      <td>林红</td>
      <td>18806817986</td>
      <td></td>
      <td>采荷中班+三班</td>
    </tr>
    <tr>
      <td>毕珊娜</td>
      <td>13757152193</td>
      <td></td>
      <td>采荷大班+五班</td>
    </tr>
    <tr>
      <td>邱懿红</td>
      <td>13758298747</td>
      <td></td>
      <td>采荷小班+二班</td>
    </tr>
    <tr>
      <td>叶识丹</td>
      <td>13758246960</td>
      <td></td>
      <td>采荷小班+一班</td>
    </tr>
    <tr>
      <td>陈琦</td>
      <td>13777861317</td>
      <td></td>
      <td>采荷中班+一班</td>
    </tr>
    <tr>
      <td>房施熠</td>
      <td>13486081434</td>
      <td></td>
      <td>采荷大班+五班</td>
    </tr>
    <tr>
      <td>夏轩</td>
      <td>13819181018</td>
      <td>副园长</td>
      <td>采荷中班+四班</td>
    </tr>
    <tr>
      <td>林洁</td>
      <td>18658888339</td>
      <td></td>
      <td>采荷中班+三班</td>
    </tr>
    <tr>
      <td>谢格恬</td>
      <td>15757902717</td>
      <td></td>
      <td>采荷大班+二班</td>
    </tr>
    <tr>
      <td>谢莲君</td>
      <td>13989456724</td>
      <td>园长</td>
      <td>采荷小班+一班</td>
    </tr>
    <tr>
      <td>王元顺</td>
      <td>15990100492</td>
      <td></td>
      <td>采荷大班+四班</td>
    </tr>
    <tr>
      <td>王芬</td>
      <td>13646841518</td>
      <td></td>
      <td>采荷中班+一班</td>
    </tr>
    <tr>
      <td>朱晓艳</td>
      <td>13023652065</td>
      <td></td>
      <td>采荷大班+一班</td>
    </tr>
    <tr>
      <td>汪天韵</td>
      <td>15397005673</td>
      <td></td>
      <td>采荷小班+四班</td>
    </tr>
    <tr>
      <td>孙丽</td>
      <td>15825504741</td>
      <td></td>
      <td>采荷大班+一班</td>
    </tr>
    <tr>
      <td>赵爱群</td>
      <td>13221096818</td>
      <td></td>
      <td>采荷大班+一班</td>
    </tr>
    <tr>
      <td>缪柳青</td>
      <td>18969968824</td>
      <td></td>
      <td>采荷小班+三班</td>
    </tr>
    <tr>
      <td>林静</td>
      <td>18758137535</td>
      <td></td>
      <td>采荷小班+四班</td>
    </tr>
    <tr>
      <td>叶夏丰</td>
      <td>13758240831</td>
      <td></td>
      <td>采荷中班+五班</td>
    </tr>
    <tr>
      <td>周婷婷</td>
      <td>17826867970</td>
      <td></td>
      <td>采荷大班+二班</td>
    </tr>
    <tr>
      <td>陈红芳</td>
      <td>13957109733</td>
      <td></td>
      <td>常青大班+三班</td>
    </tr>
    <tr>
      <td>陈琦沁</td>
      <td>19857166814</td>
      <td></td>
      <td>常青中班+二班</td>
    </tr>
    <tr>
      <td>郑晓萍</td>
      <td>15058188975</td>
      <td></td>
      <td>常青中班+三班</td>
    </tr>
    <tr>
      <td>丁婷</td>
      <td>13738032556</td>
      <td></td>
      <td>常青中班+三班</td>
    </tr>
    <tr>
      <td>程芊芊</td>
      <td>17330771960</td>
      <td></td>
      <td>常青小班+一班</td>
    </tr>
    <tr>
      <td>吕月娟</td>
      <td>13777462953</td>
      <td>副园长</td>
      <td>常青小班+一班</td>
    </tr>
    <tr>
      <td>陈露丹</td>
      <td>15168409936</td>
      <td></td>
      <td>常青大班+二班</td>
    </tr>
    <tr>
      <td>郑杭娟</td>
      <td>18626895679</td>
      <td></td>
      <td>常青小班+二班</td>
    </tr>
    <tr>
      <td>任芳</td>
      <td>13958171919</td>
      <td></td>
      <td>常青大班+一班</td>
    </tr>
    <tr>
      <td>叶菲</td>
      <td>15988174712</td>
      <td></td>
      <td>常青中班+一班</td>
    </tr>
    <tr>
      <td>吴祯</td>
      <td>13989819343</td>
      <td></td>
      <td>常青小班+一班</td>
    </tr>
    <tr>
      <td>杨艳</td>
      <td>13588190658</td>
      <td></td>
      <td>常青小班+二班</td>
    </tr>
    <tr>
      <td>叶婷婷</td>
      <td>15858139328</td>
      <td></td>
      <td>常青大班+三班</td>
    </tr>
    <tr>
      <td>黄雅雯</td>
      <td>13958161640</td>
      <td></td>
      <td>常青大班+二班</td>
    </tr>
    <tr>
      <td>许君迎</td>
      <td>15700174016</td>
      <td></td>
      <td>常青中班+二班</td>
    </tr>
    <tr>
      <td>支丽虹</td>
      <td>13606501337</td>
      <td></td>
      <td>常青大班+一班</td>
    </tr>
    <tr>
      <td>鞠云燕</td>
      <td>17857030220</td>
      <td></td>
      <td>常青中班+一班</td>
    </tr>
    <tr>
      <td>蒋士菊</td>
      <td>15805816059</td>
      <td></td>
      <td>芙蓉大班+一班</td>
    </tr>
    <tr>
      <td>姚芳</td>
      <td>15868430140</td>
      <td></td>
      <td>芙蓉大班+四班</td>
    </tr>
    <tr>
      <td>张晓芸</td>
      <td>18868785646</td>
      <td></td>
      <td>芙蓉中班+三班</td>
    </tr>
    <tr>
      <td>金双燕</td>
      <td>13486443357</td>
      <td></td>
      <td>芙蓉小班+二班</td>
    </tr>
    <tr>
      <td>杜何玉</td>
      <td>18457105753</td>
      <td></td>
      <td>芙蓉大班+一班</td>
    </tr>
    <tr>
      <td>朱早红</td>
      <td>13656675151</td>
      <td></td>
      <td>芙蓉中班+三班</td>
    </tr>
    <tr>
      <td>陈芳</td>
      <td>13567120520</td>
      <td></td>
      <td>芙蓉大班+二班</td>
    </tr>
    <tr>
      <td>周福英</td>
      <td>13065715436</td>
      <td></td>
      <td>芙蓉中班+四班</td>
    </tr>
    <tr>
      <td>许婷</td>
      <td>15669953722</td>
      <td></td>
      <td>芙蓉中班+四班</td>
    </tr>
    <tr>
      <td>周婷</td>
      <td>13967124741</td>
      <td></td>
      <td>芙蓉小班+一班</td>
    </tr>
    <tr>
      <td>马凯叶</td>
      <td>17674008141</td>
      <td></td>
      <td>芙蓉中班+二班</td>
    </tr>
    <tr>
      <td>魏静</td>
      <td>18767181808</td>
      <td></td>
      <td>芙蓉大班+三班</td>
    </tr>
    <tr>
      <td>周舟</td>
      <td>15858155823</td>
      <td></td>
      <td>芙蓉中班+一班</td>
    </tr>
    <tr>
      <td>陈平</td>
      <td>13777394818</td>
      <td></td>
      <td>芙蓉大班+三班</td>
    </tr>
    <tr>
      <td>朱芳</td>
      <td>15857132167</td>
      <td></td>
      <td>芙蓉小班+一班</td>
    </tr>
    <tr>
      <td>王静</td>
      <td>15869165061</td>
      <td></td>
      <td>芙蓉中班+二班</td>
    </tr>
    <tr>
      <td>高娟</td>
      <td>13957147412</td>
      <td></td>
      <td>芙蓉大班+四班</td>
    </tr>
    <tr>
      <td>徐欣芸</td>
      <td>18758581300</td>
      <td></td>
      <td>芙蓉小班+二班</td>
    </tr>
    <tr>
      <td>颜逍</td>
      <td>15070044472</td>
      <td></td>
      <td>芙蓉中班+一班</td>
    </tr>
    <tr>
      <td>徐薇</td>
      <td>18857559490</td>
      <td></td>
      <td>芙蓉大班+二班</td>
    </tr>
    <tr>
      <td>梁小英</td>
      <td>14758119913</td>
      <td></td>
      <td>荷花塘小班+四班</td>
    </tr>
    <tr>
      <td>叶铭涵</td>
      <td>15857187798</td>
      <td></td>
      <td>荷花塘小班+一班</td>
    </tr>
    <tr>
      <td>方楚昳</td>
      <td>13757119885</td>
      <td></td>
      <td>荷花塘小班+二班</td>
    </tr>
    <tr>
      <td>邵宇澄</td>
      <td>17398048608</td>
      <td></td>
      <td>荷花塘小班+四班</td>
    </tr>
    <tr>
      <td>黄梦媛</td>
      <td>13957159398</td>
      <td></td>
      <td>荷花塘小班+三班</td>
    </tr>
    <tr>
      <td>胡芳丽</td>
      <td>15168354102</td>
      <td></td>
      <td>荷花塘小班+一班</td>
    </tr>
    <tr>
      <td>赵君尹</td>
      <td>15257139985</td>
      <td></td>
      <td>荷花塘小班+三班</td>
    </tr>
  </tbody>
</table>
        """
        ]
    # text = """"""
    for inum, text in enumerate(ls):
        print(inum)
        chunks = text_splitter.split_text(text)
        for chunk in chunks:
            print(chunk)
