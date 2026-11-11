import FormularioUrl from "@/components/FormularioUrl";

export default function Inicio() {
  return (
    <section className="portada">
      <p className="antetitulo">Gratis · sin registro · un minuto</p>
      <h1>¿Qué está frenando a tu web?</h1>
      <p className="entradilla">
        Escribe la dirección y te decimos, sin tecnicismos, qué le impide traerte más clientes: velocidad, móvil,
        Google, textos legales y contacto.
      </p>
      <FormularioUrl />
      <ul className="ventajas">
        <li>
          <strong>Explicado para dueños de negocio</strong>
          No verás siglas: verás qué pasa, por qué importa y qué hacer.
        </li>
        <li>
          <strong>Ordenado por importancia</strong>
          Primero lo que te hace perder clientes; lo que está bien, al final.
        </li>
        <li>
          <strong>Con enlace para compartir</strong>
          Pásale el informe a quien lleve tu web.
        </li>
      </ul>
    </section>
  );
}
