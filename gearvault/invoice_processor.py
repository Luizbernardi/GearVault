"""
Módulo para processamento de invoices (notas fiscais)
Extrai informações de produtos, quantidades e valores de PDFs
"""
import re
import pdfplumber
from decimal import Decimal
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class InvoiceProcessor:
    """
    Processa invoices em PDF e extrai informações de itens da compra
    """
    
    def __init__(self, pdf_path: str):
        self.pdf_path = pdf_path
        self.text = ""
        self.items = []
    
    def extract_text(self) -> str:
        """Extrai texto do PDF usando pdfplumber"""
        try:
            with pdfplumber.open(self.pdf_path) as pdf:
                text_parts = []
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                self.text = "\n".join(text_parts)
            return self.text
        except Exception as e:
            logger.error(f"Erro ao extrair texto do PDF: {e}")
            return ""
    
    def parse_items(self) -> List[Dict]:
        """
        Analisa o texto extraído e identifica itens da nota fiscal
        Retorna lista de dicionários com: código, descrição, quantidade, valor_unitario
        
        Formato esperado: ITEM CÓDIGO DESCRIÇÃO QTDE VLR_UNIT VLR_TOTAL
        Exemplo: "001 RES-10K-0805 RESISTOR 10K OHM 0805 SMD 100 0.05 5.00"
        """
        if not self.text:
            self.extract_text()
        
        items = []
        lines = self.text.split('\n')
        
        pattern = r'(\d{3})\s+([A-Z0-9\-]+)\s+(.*?)\s+(\d+)\s+(\d+\.\d{2})\s+(\d+\.\d{2})'
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue
            
            match = re.search(pattern, line)
            if match:
                try:
                    item_num = match.group(1)
                    codigo = match.group(2)
                    descricao = match.group(3).strip()
                    quantidade = int(match.group(4))
                    valor_unitario = Decimal(match.group(5))
                    valor_total = Decimal(match.group(6))
                    
                    calculado = quantidade * valor_unitario
                    diferenca = abs(calculado - valor_total)
                    
                    if diferenca > 1:
                        logger.warning(f"Item {item_num}: Valor calculado ({calculado}) difere do total ({valor_total})")
                    
                    item = {
                        'codigo': codigo[:100],
                        'descricao': descricao[:255],
                        'quantidade': quantidade,
                        'valor_unitario': valor_unitario,
                    }
                    
                    if item['quantidade'] > 0 and item['valor_unitario'] > 0:
                        items.append(item)
                        logger.debug(f"Item extraído: {codigo} - {descricao} - Qtd: {quantidade} - Vlr: {valor_unitario}")
                
                except (ValueError, IndexError, AttributeError) as e:
                    logger.debug(f"Erro ao processar linha '{line}': {e}")
                    continue
        
        self.items = items
        logger.info(f"Total de {len(items)} itens extraídos da invoice")
        return items
    
    def extract_invoice_data(self) -> Dict:
        """
        Extrai dados completos da invoice
        Retorna dicionário com fornecedor, data, itens, etc.
        """
        if not self.text:
            self.extract_text()
        
        data = {
            'fornecedor_cnpj': self._extract_cnpj(),
            'fornecedor_nome': self._extract_fornecedor_nome(),
            'data_emissao': self._extract_data(),
            'numero_nf': self._extract_numero_nf(),
            'itens': self.parse_items(),
        }
        
        return data
    
    def _extract_cnpj(self) -> Optional[str]:
        """Extrai CNPJ do fornecedor"""
        pattern = r'CNPJ[:\s]*(\d{2}[.\s]?\d{3}[.\s]?\d{3}[/\s]?\d{4}[-\s]?\d{2})'
        match = re.search(pattern, self.text, re.IGNORECASE)
        if match:
            cnpj = re.sub(r'[^\d]', '', match.group(1))
            return cnpj if len(cnpj) == 14 else None
        return None
    
    def _extract_fornecedor_nome(self) -> Optional[str]:
        """Extrai nome do fornecedor (geralmente nas primeiras linhas)"""
        lines = self.text.split('\n')[:10]  # Primeiras 10 linhas
        for line in lines:
            if len(line) > 10 and line.isupper() and not any(word in line.lower() for word in ['cnpj', 'nota', 'fiscal']):
                return line.strip()[:255]
        return None
    
    def _extract_data(self) -> Optional[str]:
        """Extrai data de emissão"""
        pattern = r'(?:DATA|EMISS[AÃ]O)[:\s]*(\d{2}[/\-]\d{2}[/\-]\d{4})'
        match = re.search(pattern, self.text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None
    
    def _extract_numero_nf(self) -> Optional[str]:
        """Extrai número da nota fiscal"""
        pattern = r'(?:N[FºªO\.]*|NOTA)[:\s]*(\d{6,})'
        match = re.search(pattern, self.text, re.IGNORECASE)
        if match:
            return match.group(1)
        return None


def process_invoice_file(file_path: str) -> Dict:
    """
    Função utilitária para processar um arquivo de invoice
    
    Args:
        file_path: Caminho do arquivo PDF
    
    Returns:
        Dicionário com dados extraídos da invoice
    """
    processor = InvoiceProcessor(file_path)
    return processor.extract_invoice_data()


def match_products_with_database(items: List[Dict], produtos_db) -> List[Dict]:
    """
    Tenta fazer match dos itens extraídos com produtos no banco de dados
    
    Args:
        items: Lista de itens extraídos da invoice
        produtos_db: QuerySet de produtos do banco
    
    Returns:
        Lista de itens com produto_id quando encontrado match
    """
    from difflib import SequenceMatcher
    
    def similarity(a: str, b: str) -> float:
        """Calcula similaridade entre duas strings"""
        return SequenceMatcher(None, a.lower(), b.lower()).ratio()
    
    matched_items = []
    
    for item in items:
        best_match = None
        best_score = 0.0
        
        # Tenta match por código primeiro
        for produto in produtos_db:
            if produto.codigo.lower() == item['codigo'].lower():
                best_match = produto
                best_score = 1.0
                break
            
            # Tenta match por nome/descrição
            score = max(
                similarity(item['codigo'], produto.codigo),
                similarity(item['descricao'], produto.nome),
                similarity(item['codigo'], produto.nome)
            )
            
            if score > best_score and score >= 0.6:  # Threshold de 60%
                best_match = produto
                best_score = score
        
        item_matched = item.copy()
        if best_match:
            item_matched['produto_id'] = best_match.id
            item_matched['produto_nome'] = best_match.nome
            item_matched['match_score'] = best_score
        else:
            item_matched['produto_id'] = None
            item_matched['match_score'] = 0.0
        
        matched_items.append(item_matched)
    
    return matched_items
